import random
from constants.namespaces import DABGEO, OBE, OM

from locate_then_ask.ontobuiltenv.model import OBEProperty
from .address import IctAddressSynthesizer
from .measure import OmMeasureSynthesizer
from .property_usage import OBEPropertyUsageSynthesizer


class OBEPropertySynthesizer:
    def __init__(self):
        self.addr_synth = IctAddressSynthesizer()
        self.propuse_synth = OBEPropertyUsageSynthesizer()
        self.area_synth = OmMeasureSynthesizer(
            low=10, high=10000, unit=OM + "squareMetre"
        )
        self.moneyamount_synth = OmMeasureSynthesizer(
            low=100000, high=10000000, unit=OM + "poundSterling"
        )
        self.dist_synth = OmMeasureSynthesizer(low=2, high=20, unit=OM + "metre")

    def make(self):
        return OBEProperty(
            iri="placeholder",
            concept=random.choice(
                [OBE + "Property", DABGEO + "Building", OBE + "Flat"]
            ),
            address=self.addr_synth.make(),
            built_form=random.choice(
                [OBE + "Terraced", OBE + "Detached", OBE + "Semi-Detached"]
            ),
            energy_rating=random.choice("ABCDEFG"),
            latest_epc=random.choice([None, "placeholder"]),
            number_of_habitable_rooms=random.randint(1, 10),
            property_type=random.choice(
                [OBE + "ParkHome", OBE + "Maisonette", OBE + "House", OBE + "Bungalow"]
            ),
            property_usage=self.propuse_synth.make(),
            total_floor_area=self.area_synth.make(),
            market_value=self.moneyamount_synth.make(),
            latest_transaction_record=random.choice([None, "placeholder"]),
            ground_elevation=self.dist_synth.make(),
        )
