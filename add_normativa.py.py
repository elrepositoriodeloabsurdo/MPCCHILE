import json

def agregar_a_ontologia(nuevos_nodos, nuevas_relaciones):
    # 1. Cargar Ontología
    try:
        with open("ontology.json", "r", encoding="utf-8") as f:
            ontology = json.load(f)
    except FileNotFoundError:
        ontology = []

    # 2. Cargar Relaciones
    try:
        with open("relations.json", "r", encoding="utf-8") as f:
            relations = json.load(f)
    except FileNotFoundError:
        relations = []

    # Evitar duplicados por ID e inyectar nodos
    existentes_ids = {nodo["id"] for nodo in ontology}
    for nodo in nuevos_nodos:
        if nodo["id"] not in existentes_ids:
            ontology.append(nodo)
            print(f"✔ Nodo agregado: {nodo['name']}")

    # Inyectar relaciones (evitando duplicados idénticos)
    for rel in nuevas_relaciones:
        if rel not in relations:
            relations.append(rel)
            print(f"✔ Relación agregada: {rel['source']} --({rel['property']})--> {rel['target']}")

    # 3. Guardar con formato limpio
    with open("ontology.json", "w", encoding="utf-8") as f:
        json.dump(ontology, f, indent=2, ensure_ascii=False)
        
    with open("relations.json", "w", encoding="utf-8") as f:
        json.dump(relations, f, indent=2, ensure_ascii=False)

    print("\n¡Base normativa actualizada con éxito!")

# --- COPIA Y PEGA LO QUE TE DI AQUÍ ---
nodos_delitos = [
  {"id": "ley_21459", "name": "Ley N° 21.459 (Delitos Informáticos)", "branch": "delitos_informaticos", "definition": "Normativa chilena que adecua la legislación al Convenio de Budapest, tipificando delitos informáticos y estableciendo la responsabilidad penal de las personas jurídicas.", "risk_tier": "alto"},
  {"id": "acceso_ilicito", "name": "Acceso Ilícito (Art. 2)", "branch": "delitos_informaticos", "definition": "Acceder a un sistema informático sin autorización o excediendo la poseída, superando barreras técnicas o medidas tecnológicas de seguridad.", "risk_tier": "alto"},
  {"id": "falsificacion_informatica", "name": "Falsificación Informática (Art. 5)", "branch": "delitos_informaticos", "definition": "Introducción, alteración, daño o supresión indebida de datos informáticos con la intención de que sean tomados como auténticos.", "risk_tier": "alto"},
  {"id": "fraude_informatico", "name": "Fraude Informático (Art. 7)", "branch": "delitos_informaticos", "definition": "Manipulación de un sistema informático mediante introducción, alteración o supresión de datos para obtener un beneficio económico causando perjuicio a otro.", "risk_tier": "alto"},
  {"id": "preservacion_provisoria_datos", "name": "Preservación Provisoria de Datos (Art. 18 / Bis 218)", "branch": "delitos_informaticos", "definition": "Obligación impuesta a proveedores de servicios de conservar o proteger datos informáticos concretos por un periodo de hasta 90 días (prorrogable a 180) a requerimiento del Ministerio Público.", "risk_tier": "limitado"}
]

relaciones_delitos = [
  {"source": "fraude_informatico", "property": "regula", "target": "gobernanza_ia"},
  {"source": "acceso_ilicito", "property": "requiere", "target": "openfang"},
  {"source": "falsificacion_informatica", "property": "equivale_a", "target": "riesgo_alto"},
  {"source": "checkwizard", "property": "supervisa", "target": "fraude_informatico"},
  {"source": "preservacion_provisoria_datos", "property": "referencia_cruzada", "target": "brecha_de_seguridad"}
]

agregar_a_ontologia(nodos_delitos, relaciones_delitos)