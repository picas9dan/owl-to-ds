import copy
from constants.namespaces import OBE
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBEBuiltFormLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert entity.built_form is not None
        query_graph = copy.deepcopy(query_graph)

        assert entity.built_form.startswith(OBE), entity.built_form
        clsname = entity.built_form[len(OBE) :]
        clsname_node = "obe:" + clsname
        query_graph.add_node(clsname_node, iri=clsname_node, prefixed=True, template_node=True)
        query_graph.add_triple("Property", "obe:hasBuiltForm/a", clsname_node)

        verbn = "built form is " + clsname

        return query_graph, verbn