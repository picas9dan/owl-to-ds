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


OBE_PROPERTYUSAGE_LABELS = {
    "Domestic": ["domestic property", "living space"],
    "SingleResidential": ["single-residential property"],
    "MultiResidential": ["multi-residential property"],
    "Non-Domestic": ["non-domestic property", "non-living"],
    "CulturalFacility": ["cultural facility"],
    "SportsFacility": ["sports facility"],
    "TransportFacility": ["transport facility"],
    "EmergencyService": ["emergency service"],
    "PoliceStation": ["police station"],
    "FireStation": ["fire station"],
    "Hotel": ["hotel"],
    "Education": ["education"],
    "School": ["school"],
    "University": ["university"],
    "EatingEstablishment": ["eating establishment"],
    "RetailEstablishment": ["retail establishment"],
    "ReligiousFacility": ["religious facility"],
    "DrinkingEstablishment": ["drinking establishment"],
    "Bank": ["bank"],
    "Medical": ["medical facility", "healthcare facility"],
    "MedicalCare": ["medical facility", "healthcare facility"],
    "Pharmacy": ["pharmacy"],
    "Clinic": ["clinic"],
    "Hospital": ["hospital"],
    "Office": ["office"],
    "IndustrialFacility": ["industrial facility"]
}