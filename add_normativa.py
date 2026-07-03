# --- DATOS DE LA RAMA LEY MARCO DE CIBERSEGURIDAD (LEY 21.663) ---
nodos_ciberseguridad = [
  {
    "id": "ley_21663",
    "name": "Ley N° 21.663 (Ley Marco de Ciberseguridad)",
    "branch": "ciberseguridad_cl",
    "definition": "Normativa chilena que establece la institucionalidad de ciberseguridad, deberes de seguridad y notificación de incidentes para regular la resiliencia digital del país.",
    "risk_tier": "alto"
  },
  {
    "id": "anci",
    "name": "Agencia Nacional de Ciberseguridad (ANCI)",
    "branch": "ciberseguridad_cl",
    "definition": "Autoridad técnica de ciberseguridad en Chile encargada de dictar normas, fiscalizar el cumplimiento e imponer sanciones bajo la Ley 21.663.",
    "risk_tier": "alto"
  },
  {
    "id": "servicio_esencial",
    "name": "Servicio Esencial (SE)",
    "branch": "ciberseguridad_cl",
    "definition": "Servicios provistos por organismos del Estado e instituciones privadas cuya interrupción puede causar grave daño a la vida, salud o seguridad de la población.",
    "risk_tier": "alto"
  },
  {
    "id": "operador_importancia_vital",
    "name": "Operador de Importancia Vital (OIV)",
    "branch": "ciberseguridad_cl",
    "definition": "Instituciones calificadas por la ANCI que proveen servicios esenciales y dependen críticamente de las tecnologías de información para su operación.",
    "risk_tier": "alto"
  },
  {
    "id": "reporte_incidentes_ciber",
    "name": "Obligación de Reportar Incidentes (Art. 8)",
    "branch": "ciberseguridad_cl",
    "definition": "Deber legal de los OIV y SE de notificar a la ANCI todo incidente de ciberseguridad que pueda tener efectos significativos de manera inmediata (plazo máximo de 3 horas).",
    "risk_tier": "alto"
  }
]

relaciones_ciberseguridad = [
  {"source": "ley_21663", "property": "regula", "target": "gobernanza_ia"},
  {"source": "operador_importancia_vital", "property": "requiere", "target": "checkwizard"},
  {"source": "servicio_esencial", "property": "equivale_a", "target": "riesgo_alto"},
  {"source": "reporte_incidentes_ciber", "property": "referencia_cruzada", "target": "brecha_de_seguridad"},
  {"source": "anci", "property": "supervisa", "target": "operador_importancia_vital"}
]

# Ejecutamos la función pasándole los nuevos datos
agregar_a_ontologia(nodos_ciberseguridad, relaciones_ciberseguridad)
