import random
from constants.functions import NumOp
from constants.namespaces import OM
from constants.om import OM_KEY_LABELS
from constants.ontobuiltenv import OBE_ATTR_LABELS, OBEAttrKey
from locate_then_ask.ontobuiltenv.model import OmMeasure
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


class OBEOmMeasureLocator:
    def locate(self, query_graph: QueryGraph, key: OBEAttrKey, measure: OmMeasure):
        operator = random.choice(tuple(NumOp))
        operand, op_verbn = make_operand_and_verbn(
            operator, value=measure.numerical_value
        )

        bn = query_graph.make_blank_node()
        numval_node = key.value + "NumericalValue"

        func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
        func_node = "Func_" + str(func_num)
        func_label = operator.value + "\n" + str(operand)

        assert measure.unit_iri.startswith(OM), measure.unit_iri
        unit = measure.unit_iri[len(OM) :]
        unit_node = "om:" + unit
        unit_verbn = random.choice(OM_KEY_LABELS[unit])

        query_graph.add_nodes_from(
            [
                (numval_node, dict(literal=True)),
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
                (unit_node, dict(iri=unit_node, prefixed=True, template_node=True)),
            ]
        )
        query_graph.add_edges_from(
            [
                (
                    "Property",
                    bn,
                    dict(label="obe:has{key}/om:hasValue".format(key=key.value)),
                ),
                (bn, numval_node, dict(label="om:hasNumericalValue")),
                (numval_node, func_node, dict(label="func")),
                (bn, unit_node, dict(label="om:hasUnit")),
            ]
        )

        verbn = "{key} is {op} {unit}".format(
            key=random.choice(OBE_ATTR_LABELS[key]), op=op_verbn, unit=unit_verbn
        )

        return query_graph, verbn
