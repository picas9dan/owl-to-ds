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

OBE_ATTR_LABELS = {
    OBEAttrKey.ADDRESS: ["address"],
    OBEAttrKey.BUILT_FORM: ["built form"],
    OBEAttrKey.ENERGY_RATING: ["energy rating"],
    OBEAttrKey.IDENTIFIER: ["identifier"],
    OBEAttrKey.LATEST_EPC: ["latest_epc"],
    OBEAttrKey.NUMBER_OF_HABITABLE_ROOMS: ["number of habitable rooms"],
    OBEAttrKey.PROPERTY_TYPE: ["property type"],
    OBEAttrKey.PROPERTY_USAGE: ["property usage"],
    OBEAttrKey.TOTAL_FLOOR_AREA: ["total floor area"],
    OBEAttrKey.MARKET_VALUE: ["market value"],
    OBEAttrKey.GROUND_ELEVATION: ["ground elevation"],
}
