import copy
from locate_then_ask.data_model import AskDatum
from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph


class OKMechanismAsker:
    def __init__(self):
        self.graph2sparql = Graph2Sparql()

    def ask_name(self, query_graph: QueryGraph, verbalization: str):
        query_graph.add_question_node("Mechanism")
        
        query_sparql = self.graph2sparql.convert(query_graph)
        verbalization = "What is " + verbalization

        return query_sparql, verbalization
