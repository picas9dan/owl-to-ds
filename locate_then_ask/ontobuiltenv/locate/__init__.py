import random
from typing import Dict

from constants.namespaces import DABGEO, OBE
from constants.ontobuiltenv import OBEAttrKey
from locate_then_ask.query_graph import QueryGraph
from locate_then_ask.ontobuiltenv.entity_store import OBEEntityStore
from .attr import OBEAttrLocator
from .address import OBEAddressLocator
from .built_form import OBEBuiltFormLocator
from .energy_rating import OBEEnergyRatingLocator
from .ground_elevation import OBEGroundElevationLocator
from .market_value import OBEMarketValueLocator
from .number_of_habitable_rooms import OBENumOfHabitableRoomsLocator
from .property_type import OBEPropertyTypeLocator
from .property_usage import OBEPropertyUsageLocator
from .total_floor_area import OBETotalFloorAreaLocator


class OBELocator:
    def __init__(self) -> None:
        self.store = OBEEntityStore()
        self.attr_locators: Dict[OBEAttrKey, OBEAttrLocator] = {
            OBEAttrKey.ADDRESS: OBEAddressLocator(),
            OBEAttrKey.BUILT_FORM: OBEBuiltFormLocator(),
            OBEAttrKey.ENERGY_RATING: OBEEnergyRatingLocator(),
            OBEAttrKey.NUMBER_OF_HABITABLE_ROOMS: OBENumOfHabitableRoomsLocator(),
            OBEAttrKey.PROPERTY_TYPE: OBEPropertyTypeLocator(),
            OBEAttrKey.PROPERTY_USAGE: OBEPropertyUsageLocator(),
            OBEAttrKey.TOTAL_FLOOR_AREA: OBETotalFloorAreaLocator(),
            OBEAttrKey.MARKET_VALUE: OBEMarketValueLocator(),
            OBEAttrKey.GROUND_ELEVATION: OBEGroundElevationLocator(),
        }

    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_topic_node("Property", iri=entity_iri)

        entity = self.store.get(entity_iri)
        entity_cls = random.choice(entity.concepts)
        if entity_cls == DABGEO + "Building":
            query_graph.add_iri_node("dabgeo:Building", prefixed=True)
            query_graph.add_triple("Property", "a", "dabgeo:Building")

            verbalization = "building"
        elif entity_cls == OBE + "Flat":
            query_graph.add_iri_node("obe:Flat", prefixed=True)
            query_graph.add_triple("Property", "a", "obe:Flat")

            verbalization = "flat"
        elif entity_cls == OBE + "Property":
            query_graph.add_iri_node("obe:Property", prefixed=True)
            query_graph.add_triple("Property", "a/rdfs:subClassOf*", "obe:Property")

            verbalization = "property"
        else:
            raise ValueError("Unexpeced type: " + entity_cls.__name__)

        return query_graph, verbalization

    def locate_concept_and_literal_multi(self, entity_iri: str, cond_num: int = 2):
        query_graph, concept = self.locate_concept_name(entity_iri)
        entity = self.store.get(entity_iri)

        cond_verbns = []
        for k in random.sample(entity.get_nonnone_keys(), k=cond_num):
            attr_locator = self.attr_locators[k]
            cond_verbn = attr_locator.locate(query_graph, entity=entity)
            cond_verbns.append(cond_verbn)

        verbn = "{concept} whose {conds}".format(concept=concept, conds=" and ".join(cond_verbns))

        return query_graph, verbn
        