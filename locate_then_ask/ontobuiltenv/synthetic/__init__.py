import random

from locate_then_ask.ontobuiltenv.model import OBEProperty
from .address import IctAddressSynthesizer
from .measure import OmMeasureSynthesizer
from .property_usage import OBEPropertyUsageSynthesizer


class OBEPropertySynthesizer:
    def __init__(self):
        self.addr_synth = IctAddressSynthesizer()
        self.propuse_synth = OBEPropertyUsageSynthesizer()
        self.area_synth = OmMeasureSynthesizer()
        self.moneyamount_synth = OmMeasureSynthesizer()
        self.dist_synth = OmMeasureSynthesizer()

    def make(self):
        return OBEProperty(
            iri="placeholder",
            concept=random.choice(["obe:Property", "obe:Building", "obe:Flat"]),
            address=self.addr_synth.make(),
            built_form=random.choice(
                ["obe:Terraced", "obe:Detached", "obe:Semi-Detached"]
            ),
            energy_rating=random.choice("ABCDEFG"),
            latest_epc=None,
            number_of_habitable_rooms=random.randint(1, 10),
            property_type=random.choice(
                ["obe:ParkHome", "obe:Maisonette", "obe:House", "obe:Bungalow"]
            ),
            property_usage=self.propuse_synth.make(),
            total_floor_area=self.area_synth.make(),
            market_value=self.moneyamount_synth.make(),
            latest_transaction_record="placeholder",
            ground_elevation=self.dist_synth.make(),
        )
