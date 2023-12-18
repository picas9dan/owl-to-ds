import copy
import random

from constants.ontobuiltenv import OBE_ATTR_LABELS, OBEAttrKey
from locate_then_ask.data_model import AskDatum
from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph


class OBEAsker:
    def __init__(self):
        self.graph2sparql = Graph2Sparql()
        
    def ask_name(self, query_graph: QueryGraph, verbalization: str):
        query_graph = copy.deepcopy(query_graph)
        query_graph.nodes["Property"]["question_node"] = True

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What is the " + verbalization

        return AskDatum(
            query_graph=query_graph,
            query_sparql=query_sparql,
            verbalization=verbalization,
        )


    def ask_attrs(self, query_graph: QueryGraph, verbalization: str, attr_num: int = 1):
        topic_node = query_graph.get_topic_node()
        sampled_attr_keys = tuple(key for _, key in query_graph.nodes(data="key") if key is not None)
        assert all(isinstance(key, OBEAttrKey) for key in sampled_attr_keys), sampled_attr_keys

        unsampled_attr_keys = tuple(x for x in OBEAttrKey if x not in sampled_attr_keys)
        verbns = []
        for key in random.sample(unsampled_attr_keys, k=attr_num):
            query_graph.add_question_node(key.value)
            query_graph.add_triple(topic_node, "obe:has" + key.value, key.value)

            verbns.append(random.choice(OBE_ATTR_LABELS[key]))

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What is the {attrs} of the {located}".format(attrs = " and ".join(verbns), located=verbalization)

        return AskDatum(
            query_graph=query_graph,
            query_sparql=query_sparql,
            verbalization=verbalization
        )
