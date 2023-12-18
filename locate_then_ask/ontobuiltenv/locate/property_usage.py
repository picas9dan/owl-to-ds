import copy
import random

from constants.functions import NumOp
from constants.namespaces import OBE
from constants.ontobuiltenv import OBE_PROPERTYUSAGE_LABELS
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


class OBEPropertyUsageLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert any(entity.property_usage)
        query_graph = copy.deepcopy(query_graph)

        verbns = []
        samples = random.sample(
            entity.property_usage,
            k=random.choice(range(1, len(entity.property_usage) + 1)),
        )
        for use in samples:
            bn = query_graph.make_blank_node()
            assert use.concept.startswith(OBE), use.concept
            clsname = use.concept[len(OBE) :]
            clsname_node = "obe:" + clsname

            query_graph.add_node(clsname_node, iri=clsname_node, template_node=True, prefixed=True)
            query_graph.add_edges_from(
                [
                    ("Property", bn, dict(label="obe:hasPropertyUsage")),
                    (bn, clsname_node, dict(label="a/rdfs:subClassOf*")),
                ]
            )

            verbn = random.choice(OBE_PROPERTYUSAGE_LABELS[clsname])

            if use.usage_share is not None:
                operator = random.choice(tuple(NumOp))
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

                literal_node = clsname + "UsageShare"
                func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
                func_node = "Func_" + str(func_num)
                func_label = operator.value + "\n" + str(operand)

                query_graph.add_nodes_from(
                    [
                        (literal_node, dict(literal=True)),
                        (
                            func_node,
                            dict(
                                func=True,
                                template_node=True,
                                operator=operator,
                                operand=operand,
                                label=func_label,
                            ),
                        ),
                    ]
                )
                query_graph.add_edges_from(
                    [
                        (bn, literal_node, dict(label="obe:hasUsageShare")),
                        (literal_node, func_node, dict(label="func")),
                    ]
                )
                verbn = verbn + " for " + verbn_numop

            verbns.append(verbn)

        verbalization = "use is " + " and ".join(verbns)

        return query_graph, verbalization
