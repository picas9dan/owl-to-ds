import copy
from constants.ontobuiltenv import OBEAttrKey
from locate_then_ask.data_model import AskDatum
from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph, get_preds


class OBEAsker:
    def __init__(self):
        self.graph2sparql = Graph2Sparql()
        
    def ask_name(self, query_graph: QueryGraph, verbalization: str):
        query_graph = copy.deepcopy(query_graph)
        query_graph.nodes["Property"]["question_node"] = True

        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What are " + verbalization

        return AskDatum(
            query_graph=query_graph,
            query_sparql=query_sparql,
            verbalization=verbalization,
        )


    def ask_attrs(self, query_graph: QueryGraph, verbn: str):
        pass
