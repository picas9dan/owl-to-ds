from dataclasses import dataclass
from typing import Dict, List, Optional

from constants.ontospecies import OSIdentifierKey, OSPropertyKey


@dataclass
class OSProperty:
    value: float
    unit: str
    reference_state_value: Optional[float]
    reference_state_unit: Optional[str]


@dataclass
class OSSpecies:
    iri: str
    key2identifier: Dict[OSIdentifierKey, List[str]]
    key2property: Dict[OSPropertyKey, List[OSProperty]]
    chemclasses: List[str]
    uses: List[str]
