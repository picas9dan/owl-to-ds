from decimal import Decimal
import random
from locate_then_ask.ontobuiltenv.model import OmMeasure


class OmMeasureSynthesizer:
    def __init__(self, low: float, high: float, unit: str):
        self.low = low
        self.high = high
        self.unit = unit

    def make(self) -> OmMeasure:
        val = random.uniform(self.low, self.high)
        return OmMeasure(
            numerical_value=Decimal(str(round(val, 2))),
            unit_iri=self.unit,
        )
