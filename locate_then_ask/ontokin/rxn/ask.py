import random

from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph


class OKReactionAsker:
    def __init__(self):
        self.graph2sparql = Graph2Sparql()

    def ask_name(self, query_graph: QueryGraph, verbalization: str):
        query_graph.add_question_node("Reaction")

        verbalization = "What is " + verbalization
        query_sparql = self.graph2sparql.convert(query_graph)

        return query_sparql, verbalization

    def ask_count(self, query_graph: QueryGraph, verbalization: str):
        assert "Mechanism" in query_graph.nodes()

        query_graph.add_question_node("Reaction", count=True)

        if verbalization.startswith("the"):
            verbalization = verbalization[len("the") :].strip()

        verbalization = "How many {x} are there".format(x=verbalization)
        query_sparql = self.graph2sparql.convert(query_graph)

        return query_sparql, verbalization

    def ask_relation(self, query_graph: QueryGraph, verbalization: str):
        query_graph.add_question_node("KineticModel")
        query_graph.add_triple("Reaction", "okin:hasKineticModel", "KineticModel")

        template = random.choice(
            [
                "For {E}, what is its {ATTR}",
                "What is the {ATTR} of {E}",
            ]
        )
        verbalization = template.format(
            E=verbalization,
            ATTR=random.choice(
                [
                    "kinetic model",
                    "kinetic model parameters",
                    "rate constants",
                    "rate constant parameters",
                ]
            ),
        )

        if "Mechanism" in query_graph.nodes():
            query_graph.add_triple("KineticModel", "okin:definedIn", "Mechanism")

        query_sparql = self.graph2sparql.convert(query_graph)

        return query_sparql, verbalization
