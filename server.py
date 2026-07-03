"""
VibeCodingChile MCP Server
===========================

Expone la ontología de cumplimiento de VibeCodingChile (Ley N°21.719, ISO/IEC 42001,
EU AI Act y terminología propia de Gobernador IA) como herramientas, recursos y
prompts para agentes de IA vía Model Context Protocol.

Paridad de superficie con el estándar FOLIO MCP Server (12 tools, 3 resources,
11 prompts), con un diferencial propio: un grafo de propiedades tipadas
(implementa, regula, requiere, referencia_cruzada, equivale_a, ...) que mapea
explícitamente equivalencias y dependencias ENTRE los cuatro marcos normativos —
el mapeo cruzado que sostiene la arquitectura de Gobernador IA.

Uso rápido:
    uvx vibecodingchile-mcp

O agregar a Claude Code:
    claude mcp add vibecodingchile -- uvx vibecodingchile-mcp
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Optional
from xml.sax.saxutils import escape as xml_escape

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from .data_loader import store

mcp = FastMCP("vibecodingchile_mcp")


# --------------------------------------------------------------------- #
# Formatos de salida
# --------------------------------------------------------------------- #
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSONLD = "jsonld"
    OWLXML = "owlxml"


# --------------------------------------------------------------------- #
# Helpers de formato
# --------------------------------------------------------------------- #
def _concept_to_md(c: dict, include_path: bool = False) -> str:
    lines = [f"### {c['label_es']} (`{c['id']}`)"]
    if c.get("label_en"):
        lines.append(f"*{c['label_en']}*")
    lines.append("")
    lines.append(c.get("definition_es", ""))
    if c.get("aliases"):
        lines.append(f"\n**Alias:** {', '.join(c['aliases'])}")
    lines.append(f"\n**Rama:** {c['branch']} | **Marcos:** {', '.join(c.get('frameworks', []))}")
    if include_path:
        path = store.get_path(c["id"])
        breadcrumb = " → ".join(p["label_es"] for p in path)
        lines.append(f"\n**Ruta taxonómica:** {breadcrumb}")
    return "\n".join(lines)


def _concept_to_jsonld(c: dict) -> dict:
    return {
        "@context": "https://vibecodingchile.dev/context/compliance-ontology.jsonld",
        "@id": f"vcc:{c['id']}",
        "@type": "ComplianceConcept",
        "skos:prefLabel": {"es": c["label_es"], "en": c.get("label_en", "")},
        "skos:definition": {"es": c.get("definition_es", "")},
        "skos:altLabel": c.get("aliases", []),
        "vcc:branch": c["branch"],
        "vcc:frameworks": c.get("frameworks", []),
        "skos:broader": f"vcc:{c['parent']}" if c.get("parent") else None,
    }


def _concept_to_owlxml(c: dict) -> str:
    cid = xml_escape(c["id"])
    label_es = xml_escape(c["label_es"])
    label_en = xml_escape(c.get("label_en", ""))
    definition = xml_escape(c.get("definition_es", ""))
    parent_block = (
        f'\n    <rdfs:subClassOf rdf:resource="https://vibecodingchile.dev/ontology#{xml_escape(c["parent"])}"/>'
        if c.get("parent") else ""
    )
    aliases_block = "".join(
        f'\n    <skos:altLabel xml:lang="es">{xml_escape(a)}</skos:altLabel>' for a in c.get("aliases", [])
    )
    frameworks_block = "".join(
        f'\n    <vcc:framework>{xml_escape(fw)}</vcc:framework>' for fw in c.get("frameworks", [])
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#"
         xmlns:vcc="https://vibecodingchile.dev/ontology#">
  <owl:Class rdf:about="https://vibecodingchile.dev/ontology#{cid}">
    <rdfs:label xml:lang="es">{label_es}</rdfs:label>
    <rdfs:label xml:lang="en">{label_en}</rdfs:label>
    <skos:definition xml:lang="es">{definition}</skos:definition>{parent_block}{aliases_block}{frameworks_block}
  </owl:Class>
</rdf:RDF>"""


def _results_list_md(results: list, title: str) -> str:
    if not results:
        return f"## {title}\n\nSin resultados."
    lines = [f"## {title} ({len(results)})\n"]
    for c in results:
        lines.append(f"- **{c['label_es']}** (`{c['id']}`) — {c.get('definition_es', '')[:140]}...")
    return "\n".join(lines)


# --------------------------------------------------------------------- #
# Input models
# --------------------------------------------------------------------- #
class SearchConceptsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(..., description="Texto a buscar en etiquetas (es/en) y alias. Punto de entrada primario.", min_length=1, max_length=200)
    branch: Optional[str] = Field(default=None, description="Filtrar por rama: ley_21719, iso_42001, eu_ai_act, gobernanza_ia")
    limit: int = Field(default=10, ge=1, le=50)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class SearchDefinitionsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(..., description="Texto a buscar dentro del cuerpo de las definiciones (no en las etiquetas)", min_length=1, max_length=200)
    branch: Optional[str] = Field(default=None, description="Filtrar por rama")
    limit: int = Field(default=10, ge=1, le=50)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class QueryConceptsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    branch: Optional[str] = Field(default=None, description="Rama exacta a filtrar")
    framework: Optional[str] = Field(default=None, description="Marco normativo: ley_21719, iso_42001, eu_ai_act, gobernanza_ia")
    label_contains: Optional[str] = Field(default=None, description="Substring a buscar en la etiqueta en español")
    has_parent: Optional[bool] = Field(default=None, description="true = solo conceptos con padre, false = solo raíces de rama")
    limit: int = Field(default=50, ge=1, le=100)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class QueryPropertiesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    property_type: Optional[str] = Field(default=None, description="Tipo de relación: implementa, regula, requiere, referencia_cruzada, equivale_a, deriva_de, formaliza, orquesta, produce, visualiza, supervisa, reconfigura")
    from_concept: Optional[str] = Field(default=None, description="ID del concepto origen (dominio)")
    to_concept: Optional[str] = Field(default=None, description="ID del concepto destino (rango)")
    limit: int = Field(default=50, ge=1, le=100)


class GetConceptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    concept_id: str = Field(..., description="ID exacto del concepto (ej. 'base_licitud', 'riesgo_alto', 'checkwizard')")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ExportConceptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    concept_id: str = Field(..., description="ID exacto del concepto a exportar")
    format: ExportFormat = Field(default=ExportFormat.MARKDOWN, description="markdown | jsonld | owlxml")


class GetTaxonomyBranchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    branch: str = Field(..., description="ID de la rama: ley_21719, iso_42001, eu_ai_act, gobernanza_ia")


class GetChildrenInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    concept_id: str = Field(..., description="ID exacto del concepto")


class GetParentsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    concept_id: str = Field(..., description="ID exacto del concepto")


class FindConnectionsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    from_concept: str = Field(..., description="ID del concepto de partida")
    to_concept: str = Field(..., description="ID del concepto de destino")
    max_depth: int = Field(default=6, description="Máximo de saltos a explorar", ge=1, le=10)


# --------------------------------------------------------------------- #
# Tools (12 — paridad con FOLIO MCP)
# --------------------------------------------------------------------- #
_RO_ANNOTATIONS = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}


@mcp.tool(name="search_concepts", annotations={**_RO_ANNOTATIONS, "title": "Buscar conceptos por etiqueta"})
async def search_concepts(params: SearchConceptsInput) -> str:
    """Busca conceptos por etiqueta (es/en) o alias. Punto de entrada primario para explorar la ontología.

    Args:
        params (SearchConceptsInput): query, branch opcional, limit, response_format

    Returns:
        str: Lista de conceptos coincidentes en Markdown o JSON.
    """
    results = store.search_concepts(params.query, branch=params.branch, limit=params.limit)
    if params.response_format == ResponseFormat.JSON:
        return json.dumps(results, ensure_ascii=False, indent=2)
    return _results_list_md(results, f"Resultados para '{params.query}'")


@mcp.tool(name="search_definitions", annotations={**_RO_ANNOTATIONS, "title": "Buscar conceptos por texto de definición"})
async def search_definitions(params: SearchDefinitionsInput) -> str:
    """Busca conceptos cuyo texto de definición contiene la consulta (distinto de buscar por etiqueta).

    Args:
        params (SearchDefinitionsInput): query, branch opcional, limit, response_format

    Returns:
        str: Lista de conceptos cuya definición coincide, en Markdown o JSON.
    """
    results = store.search_definitions(params.query, branch=params.branch, limit=params.limit)
    if params.response_format == ResponseFormat.JSON:
        return json.dumps(results, ensure_ascii=False, indent=2)
    return _results_list_md(results, f"Definiciones que contienen '{params.query}'")


@mcp.tool(name="query_concepts", annotations={**_RO_ANNOTATIONS, "title": "Consulta avanzada con filtros componibles"})
async def query_concepts(params: QueryConceptsInput) -> str:
    """Ejecuta una consulta con filtros de texto y estructurales componibles sobre la ontología.

    Args:
        params (QueryConceptsInput): branch, framework, label_contains, has_parent, limit, response_format

    Returns:
        str: Lista de conceptos filtrados en Markdown o JSON.
    """
    results = store.query_concepts(
        branch=params.branch,
        framework=params.framework,
        label_contains=params.label_contains,
        has_parent=params.has_parent,
        limit=params.limit,
    )
    if params.response_format == ResponseFormat.JSON:
        return json.dumps(results, ensure_ascii=False, indent=2)
    return _results_list_md(results, "Resultados de consulta avanzada")


@mcp.tool(name="query_properties", annotations={**_RO_ANNOTATIONS, "title": "Consultar propiedades/relaciones tipadas"})
async def query_properties(params: QueryPropertiesInput) -> str:
    """Consulta el grafo de relaciones tipadas por tipo, dominio y/o rango.

    Diferencial central: mapea equivalencias y dependencias explícitas ENTRE los cuatro
    marcos (ej. 'eipd referencia_cruzada evaluacion_impacto_sistema_ia' conecta Ley 21.719
    con ISO 42001).

    Args:
        params (QueryPropertiesInput): property_type, from_concept, to_concept, limit

    Returns:
        str: Relaciones que cumplen los filtros, en JSON, con nota explicativa de cada una.
    """
    results = store.query_properties(
        property_type=params.property_type,
        from_concept=params.from_concept,
        to_concept=params.to_concept,
        limit=params.limit,
    )
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool(name="get_concept", annotations={**_RO_ANNOTATIONS, "title": "Obtener detalle completo de un concepto"})
async def get_concept(params: GetConceptInput) -> str:
    """Recupera el detalle completo de un concepto por su ID, incluyendo su ruta taxonómica.

    Args:
        params (GetConceptInput): concept_id, response_format

    Returns:
        str: Detalle del concepto en Markdown o JSON. Mensaje de error si no existe.
    """
    c = store.get(params.concept_id)
    if not c:
        return f"Error: no existe un concepto con id '{params.concept_id}'. Usa search_concepts para encontrar el ID correcto."
    if params.response_format == ResponseFormat.JSON:
        payload = dict(c)
        payload["path"] = [p["id"] for p in store.get_path(params.concept_id)]
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return _concept_to_md(c, include_path=True)


@mcp.tool(name="export_concept", annotations={**_RO_ANNOTATIONS, "title": "Exportar concepto (Markdown / JSON-LD / OWL XML)"})
async def export_concept(params: ExportConceptInput) -> str:
    """Exporta un concepto en el formato solicitado para integración con otros sistemas.

    Args:
        params (ExportConceptInput): concept_id, format

    Returns:
        str: Representación del concepto en el formato pedido.
    """
    c = store.get(params.concept_id)
    if not c:
        return f"Error: no existe un concepto con id '{params.concept_id}'."
    if params.format == ExportFormat.MARKDOWN:
        return _concept_to_md(c, include_path=True)
    if params.format == ExportFormat.OWLXML:
        return _concept_to_owlxml(c)
    return json.dumps(_concept_to_jsonld(c), ensure_ascii=False, indent=2)


@mcp.tool(name="list_branches", annotations={**_RO_ANNOTATIONS, "title": "Listar ramas de la taxonomía"})
async def list_branches() -> str:
    """Lista las 4 ramas de la ontología con el conteo de conceptos por rama.

    Returns:
        str: Listado en Markdown de ramas con su conteo de conceptos.
    """
    branches = store.list_branches()
    lines = ["## Ramas de la ontología VibeCodingChile\n"]
    for b in branches:
        lines.append(f"- **{b['label_es']}** (`{b['id']}`) — {b['concept_count']} conceptos")
    return "\n".join(lines)


@mcp.tool(name="get_taxonomy_branch", annotations={**_RO_ANNOTATIONS, "title": "Obtener árbol completo de una rama"})
async def get_taxonomy_branch(params: GetTaxonomyBranchInput) -> str:
    """Devuelve el árbol jerárquico completo (padre/hijo) de una rama de la ontología.

    Args:
        params (GetTaxonomyBranchInput): branch

    Returns:
        str: Árbol en JSON con estructura anidada de conceptos.
    """
    tree = store.get_taxonomy_branch(params.branch)
    if not tree:
        return f"Error: la rama '{params.branch}' no existe o no tiene conceptos raíz. Usa list_branches para ver las ramas disponibles."
    return json.dumps(tree, ensure_ascii=False, indent=2)


@mcp.tool(name="get_children", annotations={**_RO_ANNOTATIONS, "title": "Obtener conceptos hijos"})
async def get_children(params: GetChildrenInput) -> str:
    """Obtiene los conceptos hijos directos (subtipos) de un concepto en la taxonomía.

    Args:
        params (GetChildrenInput): concept_id

    Returns:
        str: Lista de conceptos hijos en JSON.
    """
    if not store.get(params.concept_id):
        return f"Error: no existe un concepto con id '{params.concept_id}'."
    return json.dumps(store.get_children(params.concept_id), ensure_ascii=False, indent=2)


@mcp.tool(name="get_parents", annotations={**_RO_ANNOTATIONS, "title": "Obtener conceptos padre"})
async def get_parents(params: GetParentsInput) -> str:
    """Obtiene el/los concepto(s) padre directo(s) de un concepto en la taxonomía.

    Args:
        params (GetParentsInput): concept_id

    Returns:
        str: Lista de conceptos padre en JSON (vacía si es raíz de rama).
    """
    if not store.get(params.concept_id):
        return f"Error: no existe un concepto con id '{params.concept_id}'."
    return json.dumps(store.get_parents(params.concept_id), ensure_ascii=False, indent=2)


@mcp.tool(name="get_properties", annotations={**_RO_ANNOTATIONS, "title": "Listar tipos de propiedad/relación"})
async def get_properties() -> str:
    """Lista todos los tipos de propiedad (relación semántica) definidos en la ontología,
    con su definición y cuántas veces se usa cada uno.

    Returns:
        str: Lista de tipos de propiedad en JSON.
    """
    return json.dumps(store.get_properties(), ensure_ascii=False, indent=2)


@mcp.tool(name="find_connections", annotations={**_RO_ANNOTATIONS, "title": "Encontrar conexión semántica entre dos conceptos"})
async def find_connections(params: FindConnectionsInput) -> str:
    """Encuentra el camino semántico más corto entre dos conceptos, combinando aristas de
    taxonomía y relaciones tipadas cross-framework.

    Args:
        params (FindConnectionsInput): from_concept, to_concept, max_depth

    Returns:
        str: Camino encontrado como lista de pasos {edge_type, concept_id} en JSON,
             o mensaje indicando que no se encontró conexión dentro del límite de saltos.
    """
    if not store.get(params.from_concept):
        return f"Error: no existe un concepto con id '{params.from_concept}'."
    if not store.get(params.to_concept):
        return f"Error: no existe un concepto con id '{params.to_concept}'."
    path = store.find_connections(params.from_concept, params.to_concept, max_depth=params.max_depth)
    if path is None:
        return f"Sin conexión encontrada entre '{params.from_concept}' y '{params.to_concept}' dentro de {params.max_depth} saltos."
    if path == []:
        return "Los conceptos de origen y destino son el mismo concepto."
    return json.dumps({"from": params.from_concept, "to": params.to_concept, "path": path}, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------- #
# Resources
# --------------------------------------------------------------------- #
@mcp.resource("vcc://branches")
async def branches_resource() -> str:
    """Índice de las 4 ramas de la taxonomía con conteo de conceptos."""
    return json.dumps(store.list_branches(), ensure_ascii=False, indent=2)


@mcp.resource("vcc://stats")
async def stats_resource() -> str:
    """Estadísticas de la ontología: versión, conteos de conceptos/relaciones/propiedades, licencia."""
    return json.dumps(store.stats(), ensure_ascii=False, indent=2)


@mcp.resource("vcc://branch/{name}")
async def branch_resource(name: str) -> str:
    """Conceptos de nivel superior de una rama específica (bajo demanda)."""
    return json.dumps(store.get_taxonomy_branch(name), ensure_ascii=False, indent=2)


# --------------------------------------------------------------------- #
# Prompts (11 — paridad con FOLIO MCP, adaptados al dominio de cumplimiento)
# --------------------------------------------------------------------- #
@mcp.prompt(name="classify-document")
def classify_document(description: str) -> str:
    """Clasifica un documento contra la ontología de cumplimiento VibeCodingChile."""
    return (
        "Clasifica el siguiente documento usando search_concepts / query_concepts sobre la "
        "ontología VibeCodingChile. Identifica: (1) marco(s) normativo(s) aplicable(s) "
        "(ley_21719 / iso_42001 / eu_ai_act), (2) rama y concepto(s) más específico(s), "
        "(3) base de licitud si corresponde, (4) nivel de riesgo EU AI Act si describe un "
        "sistema de IA.\n\nDocumento:\n" + description
    )


@mcp.prompt(name="identify-legal-basis")
def identify_legal_basis(situation: str) -> str:
    """Identifica la base de licitud aplicable a un tratamiento de datos."""
    return (
        "Usando get_taxonomy_branch(branch='ley_21719') y get_concept, identifica la base de "
        "licitud (consentimiento, ejecución contractual, obligación legal, interés legítimo) "
        "más apropiada para la siguiente situación, justificando la elección y señalando "
        "riesgos si la base es débil.\n\nSituación:\n" + situation
    )


@mcp.prompt(name="classify-actor")
def classify_actor(entity: str) -> str:
    """Clasifica un actor/entidad dentro de la cadena de responsabilidad."""
    return (
        "Clasifica la siguiente entidad/rol usando query_concepts(framework='ley_21719') y "
        "query_concepts(framework='iso_42001'): ¿es responsable de tratamiento, encargado de "
        "tratamiento, DPO, proveedor de IA, desarrollador de IA o usuario/implementador de IA? "
        "Usa find_connections si el rol cruza más de un marco.\n\nEntidad:\n" + entity
    )


@mcp.prompt(name="classify-risk-tier")
def classify_risk_tier(description: str) -> str:
    """Clasifica un sistema de IA en un nivel de riesgo EU AI Act."""
    return (
        "Usando get_taxonomy_branch(branch='eu_ai_act'), clasifica el siguiente sistema de IA "
        "en uno de los niveles de riesgo (inaceptable, alto, limitado, mínimo) y detalla las "
        "obligaciones aplicables al proveedor y/o implementador.\n\nSistema:\n" + description
    )


@mcp.prompt(name="identify-legal-authority")
def identify_legal_authority(authority: str) -> str:
    """Identifica el tipo de autoridad normativa aplicable."""
    return (
        "Identifica si la siguiente referencia corresponde a la Ley N°21.719 (estatuto), un "
        "reglamento derivado, un estándar internacional (ISO/IEC 42001) o un reglamento "
        "supranacional (EU AI Act), usando search_concepts y get_concept para fundamentar.\n\n"
        "Referencia:\n" + authority
    )


@mcp.prompt(name="classify-event")
def classify_event(event: str) -> str:
    """Clasifica un evento de cumplimiento."""
    return (
        "Clasifica el siguiente evento usando search_concepts y search_definitions sobre la "
        "ontología VibeCodingChile: ¿es una brecha de seguridad, una transferencia "
        "internacional, un ejercicio de derechos ARCO, una acción de fiscalización de la APDP, "
        "u otro? Indica las obligaciones de notificación/plazo que dispara.\n\nEvento:\n" + event
    )


@mcp.prompt(name="identify-service-type")
def identify_service_type(matter: str) -> str:
    """Identifica el tipo de servicio de cumplimiento requerido."""
    return (
        "Usando query_concepts sobre la ontología VibeCodingChile, identifica qué tipo de "
        "servicio de cumplimiento se requiere para el siguiente asunto: EIPD, redacción de "
        "DPA, evaluación de conformidad EU AI Act, auditoría ISO 42001, u otro.\n\nAsunto:\n"
        + matter
    )


@mcp.prompt(name="identify-forum-venue")
def identify_forum_venue(matter: str) -> str:
    """Identifica el organismo o foro competente."""
    return (
        "Usando search_concepts, identifica el organismo o foro competente para el siguiente "
        "asunto: ¿es la Agencia de Protección de Datos Personales (APDP), un organismo "
        "notificado de evaluación de conformidad EU AI Act, u otra instancia?\n\nAsunto:\n"
        + matter
    )


@mcp.prompt(name="identify-objective")
def identify_objective(matter: str) -> str:
    """Identifica los objetivos de cumplimiento aplicables a un asunto."""
    return (
        "Identifica los objetivos de cumplimiento normativo aplicables al siguiente asunto "
        "(ej. minimizar riesgo de sanción APDP, habilitar transferencia internacional, "
        "certificar sistema de IA de alto riesgo) usando la ontología VibeCodingChile como "
        "referencia.\n\nAsunto:\n" + matter
    )


@mcp.prompt(name="evaluate-eipd-necessity")
def evaluate_eipd_necessity(description: str) -> str:
    """Evalúa si un sistema requiere EIPD y qué elementos debe cubrir."""
    return (
        "Usando get_concept(concept_id='eipd') y query_properties(from_concept='eipd') como "
        "referencia, evalúa si el siguiente sistema requiere una Evaluación de Impacto en la "
        "Protección de Datos bajo la Ley N°21.719, y en caso afirmativo, lista los elementos "
        "mínimos que debe cubrir.\n\nSistema:\n" + description
    )


@mcp.prompt(name="identify-engagement-terms")
def identify_engagement_terms(arrangement: str) -> str:
    """Identifica los términos de encargo/DPA aplicables a una relación de tratamiento de datos."""
    return (
        "Usando get_concept(concept_id='dpa') y get_properties() como referencia, identifica "
        "los términos mínimos que debería contener el Acuerdo de Tratamiento de Datos (DPA) "
        "para el siguiente arreglo entre responsable y encargado de tratamiento.\n\n"
        "Arreglo:\n" + arrangement
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
