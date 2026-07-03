"""
Carga y utilidades de consulta sobre la ontología de cumplimiento VibeCodingChile.

La ontología combina:
- Ley N°21.719 (Protección de Datos Personales, Chile)
- ISO/IEC 42001 (Sistema de Gestión de IA)
- EU AI Act (Marco de riesgo)
- Terminología propia de Gobernador IA / VibeCodingChile

A diferencia de una taxonomía plana, esta ontología incluye un grafo de
propiedades tipadas (implementa, regula, requiere, referencia_cruzada,
equivale_a, ...) que mapea explícitamente conceptos EQUIVALENTES o
DEPENDIENTES entre los cuatro marcos normativos — el mapeo cruzado que
sostiene la arquitectura de Gobernador IA.

Fuente de datos: extraída de Gobernador IA / CheckWizard, complementada con
conceptos y relaciones construidos para asegurar cobertura completa.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

_ONTOLOGY_PATH = Path(__file__).parent / "ontology.json"
_RELATIONS_PATH = Path(__file__).parent / "relations.json"


class OntologyStore:
    """Índice en memoria de la ontología, cargado una sola vez (modo local)."""

    def __init__(self, ontology_path: Path = _ONTOLOGY_PATH, relations_path: Path = _RELATIONS_PATH) -> None:
        with open(ontology_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        with open(relations_path, "r", encoding="utf-8") as f:
            raw_rel = json.load(f)

        self.meta: Dict[str, Any] = raw["meta"]
        self.branches: List[Dict[str, Any]] = raw["branches"]
        self.concepts: Dict[str, Dict[str, Any]] = {c["id"]: c for c in raw["concepts"]}

        self.property_types: Dict[str, Dict[str, Any]] = {
            p["id"]: p for p in raw_rel["property_types"]
        }
        self.relations: List[Dict[str, Any]] = raw_rel["relations"]

        # Índice de hijos por parent_id (taxonomía)
        self.children_index: Dict[str, List[str]] = {}
        for cid, c in self.concepts.items():
            parent = c.get("parent")
            if parent:
                self.children_index.setdefault(parent, []).append(cid)

        # Índice de relaciones tipadas: salientes y entrantes
        self.relations_out: Dict[str, List[Dict[str, Any]]] = {}
        self.relations_in: Dict[str, List[Dict[str, Any]]] = {}
        for r in self.relations:
            self.relations_out.setdefault(r["from"], []).append(r)
            self.relations_in.setdefault(r["to"], []).append(r)

    # ---------------------------------------------------------------- #
    # Búsqueda
    # ---------------------------------------------------------------- #
    def search_concepts(
        self, query: str, branch: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Búsqueda primaria por etiqueta (es/en) y alias. Prioriza coincidencias de label."""
        q = query.strip().lower()
        results = []
        for c in self.concepts.values():
            if branch and c["branch"] != branch:
                continue
            label_hit = q in c.get("label_es", "").lower() or q in c.get("label_en", "").lower()
            alias_hit = any(q in a.lower() for a in c.get("aliases", []))
            if label_hit or alias_hit:
                score = 2 if label_hit else 1
                results.append((score, c))
        results.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in results[:limit]]

    def search_definitions(
        self, query: str, branch: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Búsqueda específica sobre el texto de la definición (definition_es)."""
        q = query.strip().lower()
        results = []
        for c in self.concepts.values():
            if branch and c["branch"] != branch:
                continue
            if q in c.get("definition_es", "").lower():
                results.append(c)
        return results[:limit]

    def query_concepts(
        self,
        branch: Optional[str] = None,
        framework: Optional[str] = None,
        label_contains: Optional[str] = None,
        has_parent: Optional[bool] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Filtros componibles estructurales + texto sobre la ontología."""
        out = []
        for c in self.concepts.values():
            if branch and c["branch"] != branch:
                continue
            if framework and framework not in c.get("frameworks", []):
                continue
            if label_contains and label_contains.lower() not in c.get("label_es", "").lower():
                continue
            if has_parent is not None:
                if has_parent and not c.get("parent"):
                    continue
                if not has_parent and c.get("parent"):
                    continue
            out.append(c)
        return out[:limit]

    # ---------------------------------------------------------------- #
    # Detalle y taxonomía
    # ---------------------------------------------------------------- #
    def get(self, concept_id: str) -> Optional[Dict[str, Any]]:
        return self.concepts.get(concept_id)

    def get_children(self, concept_id: str) -> List[Dict[str, Any]]:
        return [self.concepts[cid] for cid in self.children_index.get(concept_id, [])]

    def get_parents(self, concept_id: str) -> List[Dict[str, Any]]:
        """Lista de padres directos (en esta ontología: 0 o 1, jerarquía estricta)."""
        c = self.concepts.get(concept_id)
        if not c or not c.get("parent"):
            return []
        parent = self.concepts.get(c["parent"])
        return [parent] if parent else []

    def get_path(self, concept_id: str) -> List[Dict[str, Any]]:
        path = []
        current = self.concepts.get(concept_id)
        while current:
            path.append(current)
            parent_id = current.get("parent")
            current = self.concepts.get(parent_id) if parent_id else None
        return list(reversed(path))

    # ---------------------------------------------------------------- #
    # Propiedades tipadas (relaciones semánticas cross-framework)
    # ---------------------------------------------------------------- #
    def get_properties(self) -> List[Dict[str, Any]]:
        """Lista los tipos de propiedad/relación definidos, con conteo de uso."""
        out = []
        for pid, p in self.property_types.items():
            count = sum(1 for r in self.relations if r["type"] == pid)
            out.append({**p, "usage_count": count})
        return out

    def query_properties(
        self,
        property_type: Optional[str] = None,
        from_concept: Optional[str] = None,
        to_concept: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Filtra relaciones tipadas por tipo, concepto origen y/o concepto destino."""
        out = []
        for r in self.relations:
            if property_type and r["type"] != property_type:
                continue
            if from_concept and r["from"] != from_concept:
                continue
            if to_concept and r["to"] != to_concept:
                continue
            out.append(r)
        return out[:limit]

    def get_relations_for(self, concept_id: str) -> Dict[str, Any]:
        return {
            "outgoing": self.relations_out.get(concept_id, []),
            "incoming": self.relations_in.get(concept_id, []),
        }

    def get_related(self, concept_id: str) -> Dict[str, Any]:
        c = self.concepts.get(concept_id)
        if not c:
            return {}
        return {
            "concept": c,
            "parents": self.get_parents(concept_id),
            "children": self.get_children(concept_id),
            "path": self.get_path(concept_id),
            "typed_relations": self.get_relations_for(concept_id),
        }

    # ---------------------------------------------------------------- #
    # find_connections: BFS sobre grafo combinado (taxonomía + relaciones tipadas)
    # ---------------------------------------------------------------- #
    def find_connections(self, from_id: str, to_id: str, max_depth: int = 6) -> Optional[List[Dict[str, Any]]]:
        """Encuentra el camino semántico más corto entre dos conceptos, combinando
        aristas de taxonomía (es_subtipo_de / tiene_subtipo) y relaciones tipadas
        (implementa, regula, requiere, referencia_cruzada, ...), en cualquier dirección.

        Retorna la lista de pasos (edge_type, concept_id) o None si no hay conexión
        dentro de max_depth saltos.
        """
        if from_id not in self.concepts or to_id not in self.concepts:
            return None
        if from_id == to_id:
            return []

        def neighbors(cid: str) -> List[tuple]:
            out = []
            c = self.concepts.get(cid)
            if c and c.get("parent"):
                out.append(("es_subtipo_de", c["parent"]))
            for child_id in self.children_index.get(cid, []):
                out.append(("tiene_subtipo", child_id))
            for r in self.relations_out.get(cid, []):
                out.append((r["type"], r["to"]))
            for r in self.relations_in.get(cid, []):
                out.append((f"{r['type']}_inverso", r["from"]))
            return out

        visited = {from_id}
        queue = deque([(from_id, [])])
        while queue:
            current, path = queue.popleft()
            if len(path) >= max_depth:
                continue
            for edge_type, nxt in neighbors(current):
                if nxt in visited:
                    continue
                new_path = path + [{"edge_type": edge_type, "concept_id": nxt}]
                if nxt == to_id:
                    return new_path
                visited.add(nxt)
                queue.append((nxt, new_path))
        return None

    # ---------------------------------------------------------------- #
    # Ramas
    # ---------------------------------------------------------------- #
    def list_branches(self) -> List[Dict[str, Any]]:
        out = []
        for b in self.branches:
            count = sum(1 for c in self.concepts.values() if c["branch"] == b["id"])
            out.append({**b, "concept_count": count})
        return out

    def get_taxonomy_branch(self, branch_id: str) -> List[Dict[str, Any]]:
        roots = [
            c for c in self.concepts.values()
            if c["branch"] == branch_id and c.get("parent") is None
        ]

        def build_tree(node: Dict[str, Any]) -> Dict[str, Any]:
            children = self.get_children(node["id"])
            return {
                "id": node["id"],
                "label_es": node["label_es"],
                "label_en": node.get("label_en", ""),
                "children": [build_tree(ch) for ch in children],
            }

        return [build_tree(r) for r in roots]

    # ---------------------------------------------------------------- #
    # Estadísticas
    # ---------------------------------------------------------------- #
    def stats(self) -> Dict[str, Any]:
        return {
            "name": self.meta["name"],
            "version": self.meta["version"],
            "source": self.meta["source"],
            "concept_count": len(self.concepts),
            "branch_count": len(self.branches),
            "relation_count": len(self.relations),
            "property_type_count": len(self.property_types),
            "frameworks": self.meta["frameworks"],
            "languages": self.meta["languages"],
        }


# Instancia global (modo local: se carga una sola vez al iniciar el server)
store = OntologyStore()
