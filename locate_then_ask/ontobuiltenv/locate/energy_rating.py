import copy

from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBEEnergyRatingLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert entity.energy_rating is not None
        query_graph = copy.deepcopy(query_graph)

        literal_node = query_graph.make_literal_node(entity.energy_rating)
        query_graph.add_edge("Property", literal_node, label="obe:hasEnergyRating")

        verbn = "energy rating is [{label}]".format(label=entity.energy_rating)

        return query_graph, verbn
