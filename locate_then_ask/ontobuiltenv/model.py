from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass 
class IcontactAddress:
    street: Optional[str]                       # ict:hasStreet
    street_number: Optional[str]                # ict:hasStreetNumber
    unit_name: Optional[str]                    # obe:hasUnitName
    postal_code: Optional[str]                  # obe:hasPostalCode/rdfs:label

class ObeBuiltForm(Enum):                       
    TERRACED = "Terraced"
    DETACHED = "Detached"
    SEMIDETTACHED = "Semi-Detached"

class ObePropertyType(Enum):
    HOUSE = "House"
    BUNGALOW = "Bungalow"
    PARKHOME = "ParkHome"
    MAISONETTE = "Maisonette"

@dataclass
class OmMeasure:
    numerical_value: float                      # om:hasNumericalValue
    unit_iri: str                               # om:hasUnit

@dataclass
class ObeProperty:
    address: Optional[IcontactAddress]          # obe:hasAddress 0..1 
    built_form: Optional[ObeBuiltForm]          # obe:hasBuiltForm/a obe:{value} 0..1
    # construction_component: List[str]           # obe:hasConstructionComponent 0..4
    # construction_date: Optional[str]            # obe:hasConstructionDate 0..1
    energy_rating: Optional[str]                # obe:hasEnegyRating 0..1
    identifier: Optional[str]                   # obe:hasIdentifier 0..1
    latest_epc: Optional[str]                   # obe:hasLatestEPC 0..1
    number_of_habitable_rooms: Optional[int]    # obe:hasNumberOfHabitableRooms 0..1
    property_type: Optional[ObePropertyType]    # obe:hasPropertyType 0..1
    property_usage: List[str]                   # obe:hasPropertyUsage/a*/rdfs:label 0..2
    total_floor_area: Optional[OmMeasure]       # obe:hasTotalFloorArea/om:hasValue 0..1
    # is_in: Optional[str]                        # obe:isIn 0..1
    # located_in: Optional[str]                   # obe:locatedIn 0..1
    market_value: Optional[OmMeasure]           # obe:hasMarketValue/om:hasValue 0..1
    # latest_transaction_record: Optional[str]    # obe:hasLatestTransactionRecord 0..1

@dataclass
class ObeFlat(ObeProperty):
    pass

@dataclass
class DabgeoBuilding(ObeProperty):
    ground_elevation: Optional[OmMeasure]       # obe:hasGroundElevation/om:hasValue
