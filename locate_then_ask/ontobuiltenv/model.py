from dataclasses import dataclass
from typing import List, Optional

from constants.ontobuiltenv import OBEAttrKey


@dataclass 
class IctAddress:
    street: Optional[str]                       # ict:hasStreet
    street_number: Optional[str]                # ict:hasStreetNumber
    unit_name: Optional[str]                    # obe:hasUnitName
    postal_code: Optional[str]                  # obe:hasPostalCode/rdfs:label

@dataclass
class OmMeasure:
    numerical_value: float                      # om:hasNumericalValue
    unit_iri: str                               # om:hasUnit

@dataclass
class OBEProperty:
    iri: str
    concepts: List[str]                         # a/rdfs:subClassOf*
    address: Optional[IctAddress]               # obe:hasAddress 0..1 
    built_form: Optional[str]                   # obe:hasBuiltForm/a 0..1
    # construction_component: List[str]           # obe:hasConstructionComponent 0..4
    # construction_date: Optional[str]            # obe:hasConstructionDate 0..1
    energy_rating: Optional[str]                # obe:hasEnegyRating 0..1
    # identifier: Optional[str]                   # obe:hasIdentifier 0..1
    # latest_epc: Optional[str]                   # obe:hasLatestEPC 0..1
    number_of_habitable_rooms: Optional[int]    # obe:hasNumberOfHabitableRooms 0..1
    property_type: Optional[str]                # obe:hasPropertyType/a 0..1
    property_usage: List[str]                   # obe:hasPropertyUsage/a*/rdfs:label 0..2
    total_floor_area: Optional[OmMeasure]       # obe:hasTotalFloorArea/om:hasValue 0..1
    # is_in: Optional[str]                        # obe:isIn 0..1
    # located_in: Optional[str]                   # obe:locatedIn 0..1
    market_value: Optional[OmMeasure]           # obe:hasMarketValue/om:hasValue 0..1
    # latest_transaction_record: Optional[str]    # obe:hasLatestTransactionRecord 0..1
    ground_elevation: Optional[OmMeasure]       # obe:hasGroundElevation/om:hasValue, only for dabgeo:Building

    def get_nonnone_keys(self):
        keys: List[OBEAttrKey] = []

        if self.address is not None:
            keys.append(OBEAttrKey.ADDRESS)
        if self.built_form is not None:
            keys.append(OBEAttrKey.BUILT_FORM)
        if self.energy_rating is not None:
            keys.append(OBEAttrKey.ENERGY_RATING)
        if self.latest_epc is not None:
            keys.append(OBEAttrKey.LATEST_EPC)
        if self.number_of_habitable_rooms is not None:
            keys.append(OBEAttrKey.NUMBER_OF_HABITABLE_ROOMS)
        if self.property_type is not None:
            keys.append(OBEAttrKey.PROPERTY_TYPE)
        if len(self.property_usage) > 0:
            keys.append(OBEAttrKey.PROPERTY_USAGE)
        if self.total_floor_area is not None:
            keys.append(OBEAttrKey.TOTAL_FLOOR_AREA)
        if self.market_value is not None:
            keys.append(OBEAttrKey.MARKET_VALUE)
        if self.ground_elevation is not None:
            keys.append(OBEAttrKey.GROUND_ELEVATION)

        return tuple(keys)