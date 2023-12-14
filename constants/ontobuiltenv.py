from enum import Enum


class OBEAttrKey(Enum):
    ADDRESS = "Address"
    BUILT_FORM = "BuiltForm"
    ENERGY_RATING = "EnergyRating"
    IDENTIFIER = "Identifier"
    LATEST_EPC = "LatestEPC"
    NUMBER_OF_HABITABLE_ROOMS = "NumberOfHabitableRooms"
    PROPERTY_TYPE = "PropertyType"
    PROPERTY_USAGE = "PropertyUsage"
    TOTAL_FLOOR_AREA = "TotalFloorArea"
    MARKET_VALUE = "MarketValue"
    GROUND_ELEVATION = "GroundElevation"


OBE_ATTR_KEYS = [e.value for e in OBEAttrKey]
