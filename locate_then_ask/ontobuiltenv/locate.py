from locate_then_ask.ontobuiltenv.entity_store import OBEEntityStore
from locate_then_ask.ontobuiltenv.model import DabgeoBuilding, OBEFlat, OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBELocator:
    def __init__(self) -> None:
        self.store = OBEEntityStore()
        
    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_node("Property")

        entity_cls = self.store.get_cls(entity_iri)
        if entity_cls is DabgeoBuilding:
            query_graph.add_node("dabgeo:Building", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "dabgeo:Building", label="a")

            verbalization = "building"
        elif entity_cls is OBEFlat:
            query_graph.add_node("obe:Flat", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "obe:Flat", label="a")

            verbalization = "flat"
        elif entity_cls is OBEProperty:
            query_graph.add_node("obe:Property", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "obe:Property", label="a/rdfs:subClassOf*")

            verbalization = "property"
        else:
            raise ValueError("Unexpeced type: " + entity_cls.__name__)
        
        return query_graph, verbalization