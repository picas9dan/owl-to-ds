import copy
import random

from constants.ontobuiltenv import OBE_ATTR_LABELS, OBEAttrKey
from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph


class OBEAsker:
    def __init__(self):
        self.graph2sparql = Graph2Sparql()
        
    def ask_name(self, query_graph: QueryGraph, verbalization: str):
        query_graph.add_question_node("Property")

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What is the " + verbalization

        return query_sparql, verbalization
    
    def ask_count(self, query_graph: QueryGraph, verbalization: str):
        query_graph.add_question_node("Property", count=True)

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "How many {located} are there?".format(located=verbalization)

        return query_sparql, verbalization

    def ask_attrs(self, query_graph: QueryGraph, verbalization: str, attr_num: int = 1):
        sampled_attr_keys = tuple(key for _, key in query_graph.nodes(data="key") if key is not None)
        assert all(isinstance(key, OBEAttrKey) for key in sampled_attr_keys), sampled_attr_keys

        unsampled_attr_keys = tuple(x for x in OBEAttrKey if x not in sampled_attr_keys)
        verbns = []
        for key in random.sample(unsampled_attr_keys, k=attr_num):
            query_graph.add_question_node(key.value)
            query_graph.add_triple("Property", "obe:has" + key.value, key.value)

            verbns.append(random.choice(OBE_ATTR_LABELS[key]))

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What is the {attrs} of the {located}".format(attrs = " and ".join(verbns), located=verbalization)

        return query_sparql, verbalization
