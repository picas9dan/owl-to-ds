import random
from constants.functions import AGG_OP_LABELS, AggOp

from constants.ontobuiltenv import OBE_ATTR_LABELS, OBEAttrKey
from locate_then_ask.graph2sparql import Graph2Sparql
from locate_then_ask.query_graph import QueryGraph


class OBEAsker:
    KEYS_FOR_AVG = [
        OBEAttrKey.TOTAL_FLOOR_AREA,
        OBEAttrKey.MARKET_VALUE,
        OBEAttrKey.GROUND_ELEVATION,
    ]

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
        template = random.choice(
            [
                "How many {located} are there",
                "For {located}, how many of them are there",
            ]
        )
        verbalization = template.format(located=verbalization)

        return query_sparql, verbalization

    def ask_attrs(self, query_graph: QueryGraph, verbalization: str, attr_num: int = 1):
        sampled_attr_keys = tuple(
            key for _, key in query_graph.nodes(data="key") if key is not None
        )
        assert all(
            isinstance(key, OBEAttrKey) for key in sampled_attr_keys
        ), sampled_attr_keys

        unsampled_attr_keys = tuple(x for x in OBEAttrKey if x not in sampled_attr_keys)
        verbns = []
        for key in random.sample(unsampled_attr_keys, k=attr_num):
            if key is OBEAttrKey.ADDRESS:
                q = random.choice(["address", "postalcode", "street"])
                if q == "address":
                    query_graph.add_question_node("Address")
                    query_graph.add_triple("Property", "obe:hasAddress", "Address")

                    verbns.append(random.choice(OBE_ATTR_LABELS[key]))
                elif q == "postalcode":
                    query_graph.add_question_node("PostalCode")
                    query_graph.add_triple(
                        "Property", "obe:hasAddress/obe:hasPostalCode", "PostalCode"
                    )

                    verbns.append("postal code")
                elif q == "street":
                    query_graph.add_question_node("Street")
                    query_graph.add_triple(
                        "Property", "obe:hasAddress/ict:hasStreet", "Street"
                    )

                    verbns.append("street")
                else:
                    raise Exception("Unexpected value: " + q)
            else:
                query_graph.add_question_node(key.value)
                query_graph.add_triple("Property", "obe:has" + key.value, key.value)

                verbns.append(random.choice(OBE_ATTR_LABELS[key]))

        query_sparql = self.graph2sparql.convert(query_graph)
        template = random.choice(
            [
                "What is the {attrs} of the {located}",
                "For the {located}, what is its {attrs}",
            ]
        )
        verbalization = template.format(
            attrs=" and ".join(verbns), located=verbalization
        )

        return query_sparql, verbalization

    def ask_agg(self, query_graph: QueryGraph, verbalization: str, attr_num: int = 1):
        sampled_attr_keys = tuple(
            key for _, key in query_graph.nodes(data="key") if key is not None
        )
        assert all(
            isinstance(key, OBEAttrKey) for key in sampled_attr_keys
        ), sampled_attr_keys

        candidates = [k for k in self.KEYS_FOR_AVG if k not in sampled_attr_keys]
        assert len(candidates) > 0

        verbns = []
        for key in random.sample(candidates, k=min(len(candidates, attr_num))):
            agg = random.choice(tuple(AggOp))

            bn = query_graph.make_blank_node()
            value_node = key.value + "NumericalValue"
            unit = query_graph.add_iri_node("om:poundSterling", prefixed=True)
            query_graph.add_triples(
                [
                    ("Property", "obe:has{key}/om:hasValue".format(key=key.value), bn),
                    (bn, "om:hasNumericalValue", value_node),
                    (bn, "om:hasUnit", unit),
                ]
            )
            query_graph.add_question_node(value_node, agg=agg)

            template = "{modifier} {attr}"
            verbn = template.format(
                modifier=random.choice(random.choice(AGG_OP_LABELS[agg])),
                attrs=random.choice(OBE_ATTR_LABELS[key]),
            )
            verbns.append(verbn)

        query_sparql = self.graph2sparql.convert(query_graph)
        template = random.choice(
            [
                "What is the {attrs} of the {located}",
                "For the {located}, what is its {attrs}",
            ]
        )
        verbalization = template.format(
            attrs=" and ".join(verbns),
            located=verbalization,
        )

        return query_sparql, verbalization
