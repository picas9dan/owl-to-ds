import copy

from constants.namespaces import OBE
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBEPropertyTypeLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert entity.property_type is not None
        query_graph = copy.deepcopy(query_graph)

        assert entity.property_type.startswith(OBE)
        clsname = entity.property_type[len(OBE):]
        clsname_node = "obe:" + clsname
        query_graph.add_node(
            clsname_node, iri=clsname_node, prefixed=True, template_node=True
        )
        query_graph.add_edge(
            "Property", clsname_node, label="obe:hasPropertyType/a"
        )

        verbn = "property type is " + clsname

        return query_graph, verbn
