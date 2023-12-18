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

        numofhabitableroom_node = "NumberOfHabitableRooms"
        query_graph.add_literal_node(numofhabitableroom_node)
        func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
        func_node = "Func_" + str(func_num)
        func_label = operator.value + "\n" + str(operand)

        query_graph.add_node(
            func_node,
            func=True,
            template_node=True,
            operator=operator,
            operand=operand,
            label=func_label,
        )
        query_graph.add_triples(
            [
                ("Property", "obe:hasNumberOfHabitableRooms", numofhabitableroom_node),
                (numofhabitableroom_node, "func", func_node),
            ]
        )

        verbn = "number of habitable room is " + verbn

        return query_graph, verbn
