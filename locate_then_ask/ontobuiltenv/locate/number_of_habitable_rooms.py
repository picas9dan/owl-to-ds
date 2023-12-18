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

        query_graph.add_func(
            target_node=numofhabitableroom_node,
            operator=operator,
            operand=operand
        )
        query_graph.add_triple("Property", "obe:hasNumberOfHabitableRooms", numofhabitableroom_node)
        
        verbn = "number of habitable room is " + verbn

        return query_graph, verbn
