import copy
import random

from constants.functions import NumOp
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


class OBENumOfHabitableRoomsLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert entity.number_of_habitable_rooms is not None
        query_graph = copy.deepcopy(query_graph)
        
        operator = random.choice(tuple(NumOp))
        operand, verbn = make_operand_and_verbn(
            operator, value=entity.number_of_habitable_rooms, to_int=True
        )

        literal_node = "NumberOfHabitableRooms"
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
                ("Property", literal_node, dict(label="obe:hasNumberOfHabitableRooms")),
                (literal_node, func_node, dict(label="func")),
            ]
        )

        verbn = "number of habitable room is " + verbn

        return query_graph, verbn
