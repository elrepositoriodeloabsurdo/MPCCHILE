# VibeCodingChile MCP Server

Servidor MCP (Model Context Protocol) que expone la **ontología de cumplimiento de
VibeCodingChile** —Ley N°21.719, ISO/IEC 42001, EU AI Act y la terminología propia
de Gobernador IA (NORMA, CheckWizard, OpenFang, Trust Score, etc.)— directamente a
agentes de IA como Claude Code, Gemini CLI y OpenAI Codex.

I con foco 100% en cumplimiento normativo chileno de IA y protección de datos.

## Quick start

```bash
claude mcp add vibecodingchile -- uvx vibecodingchile-mcp
```

Gemini CLI:
```bash
gemini mcp add vibecodingchile uvx vibecodingchile-mcp
```

OpenAI Codex:
```bash
codex mcp add vibecodingchile -- uvx vibecodingchile-mcp
```

Modo local (sin instalar, para desarrollo):
```bash
cd vibecodingchile-mcp
pip install -e . --break-system-packages
python -m vibecodingchile_mcp.server
```

## Qué expone

Paridad de superficie 1:1 con el estándar FOLIO MCP Server: **12 herramientas, 3 recursos, 11 prompts.**

**12 herramientas:** `search_concepts`, `search_definitions`, `query_concepts`,
`query_properties`, `get_concept`, `export_concept` (Markdown / JSON-LD / **OWL XML**),
`list_branches`, `get_taxonomy_branch`, `get_children`, `get_parents`, `get_properties`,
`find_connections`.

**3 recursos:** `vcc://branches`, `vcc://stats`, `vcc://branch/{name}`.

**11 prompts:** `classify-document`, `identify-legal-basis`, `classify-actor`,
`classify-risk-tier`, `identify-legal-authority`, `classify-event`,
`identify-service-type`, `identify-forum-venue`, `identify-objective`,
`evaluate-eipd-necessity`, `identify-engagement-terms`.

## El diferencial real: propiedades tipadas cross-framework

FOLIO es una taxonomía plana (padre/hijo). Esta ontología además incluye un grafo de
relaciones semánticas tipadas entre los 4 marcos — 12 tipos de propiedad (`implementa`,
`regula`, `requiere`, `referencia_cruzada`, `equivale_a`, `deriva_de`, `formaliza`,
`orquesta`, `produce`, `visualiza`, `supervisa`, `reconfigura`) que conectan marcos
distintos entre sí, por ejemplo:

```
eipd --requiere--> riesgo_alto
```
Un sistema de IA de alto riesgo (EU AI Act) dispara la obligación de EIPD (Ley 21.719)
— dos marcos normativos distintos conectados en un salto, vía `find_connections`.

```
checkwizard --implementa--> accountability_inverso --reconfigura--> base_licitud
```
Muestra cómo el motor de validación Rust materializa técnicamente el marco doctrinal de
accountability inverso, que a su vez reconfigura la lógica tradicional de bases de licitud.

## Las 4 ramas

| Rama | Marco | Conceptos clave |
|---|---|---|
| `ley_21719` | Ley N°21.719 (Chile) | base de licitud, derechos ARCO, EIPD, DPA, APDP, brecha de seguridad |
| `iso_42001` | ISO/IEC 42001 | proveedor/desarrollador/usuario de IA, evaluación de riesgo, supervisión humana |
| `eu_ai_act` | EU AI Act | riesgo inaceptable/alto/limitado/mínimo, obligaciones proveedor/implementador, GPAI |
| `gobernanza_ia` | Terminología propia | NORMA, OpenFang, CheckWizard, HITL, Trust Score, Doer-Verifier, accountability inverso |

## Ejemplo

Preguntale a tu agente: *"Busca en VibeCodingChile 'base de licitud'"*

El agente:
1. Llama `vcc_search_concept(query="base de licitud")`
2. Encuentra el concepto raíz y sus 4 sub-bases (consentimiento, interés legítimo, ejecución contractual, obligación legal)
3. Puede recorrer la taxonomía con `vcc_get_relations` o exportar con `vcc_export_concept`

Todo esto ocurre dentro de la conversación — sin copiar/pegar desde documentación externa.

## Arquitectura

- **Modo local** (actual): la ontología completa (`ontology.json`) se carga en memoria al iniciar. Sin dependencias externas, sin API key.
- **Modo API** (roadmap): cliente liviano contra un endpoint REST propio, para mantener la ontología sincronizada con Gobernador IA / CheckWizard en producción.

## Origen de los datos

La ontología combina conceptos extraídos directamente de la arquitectura y documentación
de Gobernador IA / CheckWizard, complementados con conceptos construidos para asegurar
cobertura completa de los tres marcos normativos (Ley 21.719, ISO 42001, EU AI Act).

## Licencia

CC BY 4.0 — VibeCodingChile
