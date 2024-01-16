from decimal import Decimal
import random

from constants.functions import PRIMITIVE_NUM_OPS, NumOp
from constants.namespaces import OBE
from constants.ontobuiltenv import OBE_PROPERTYUSAGE_LABELS, OBEAttrKey
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


class OBEPropertyUsageLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert any(entity.property_usage)

        verbns = []
        samples = random.sample(
            entity.property_usage,
            k=random.randint(1, min(len(entity.property_usage), 2)),
        )
        assert len(samples) == len(set(samples))
        for use in samples:
            usage_node = query_graph.make_blank_node(key=OBEAttrKey.PROPERTY_USAGE)
            assert use.concept.startswith(OBE), use.concept
            clsname = use.concept[len(OBE) :]
            clsname_node = "obe:" + clsname

            query_graph.add_iri_node(clsname_node, prefixed=True)
            query_graph.add_triples(
                [
                    ("Property", "obe:hasPropertyUsage", usage_node),
                    (usage_node, "a/rdfs:subClassOf*", clsname_node),
                ]
            )

            verbn = random.choice(OBE_PROPERTYUSAGE_LABELS[clsname])

            if use.usage_share is not None and random.getrandbits(1):
                if use.usage_share == Decimal("1."):
                    sampling_frame = [
                        NumOp.GREATER_THAN,
                        NumOp.GREATER_THAN_EQUAL,
                        NumOp.EQUAL,
                    ]
                else:
                    sampling_frame = PRIMITIVE_NUM_OPS
                operator = random.choice(sampling_frame)
                share_pctg = use.usage_share * 100

                operand, verbn_numop = make_operand_and_verbn(
                    operator,
                    value=share_pctg,
                    min_val=share_pctg / 2,
                    max_val=(100 + share_pctg) / 2,
                )

                if operator == NumOp.EQUAL:
                    verbn_numop = str(operand)

                share_pctg_str = str(operand)
                if share_pctg_str.endswith("00"):
                    share_pctg_str = share_pctg_str[:-2]
                share_pctg_str += "%"
                verbn_numop = verbn_numop.replace(str(operand), share_pctg_str)
                operand = operand / 100

                usageshare_node = clsname + "UsageShare"
                query_graph.add_literal_node(usageshare_node)
                query_graph.add_triple(usage_node, "obe:hasUsageShare", usageshare_node)
                query_graph.add_func(
                    target_node=usageshare_node, operator=operator, operand=operand
                )

                verbn = verbn + " for " + verbn_numop

            verbns.append(verbn)

        verbalization = "usage is " + ", ".join(verbns)

        return verbalization
