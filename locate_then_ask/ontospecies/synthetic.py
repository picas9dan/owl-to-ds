import json
import os
import random
from typing import Dict, Tuple

from constants.ontospecies import OSIdentifierKey, OSPropertyKey
from .model import OSSpecies
from constants.fs import ROOTDIR


class OSPropertySynthesizer:
    PROPERTY_BOUNDS_FILEPATH = "data/ontospecies/PropertyBounds.json"
    INT_PROPERTIES = [
        OSPropertyKey.ATOM_CHIRAL_COUNT,
        OSPropertyKey.ATOM_CHIRAL_DEF_COUNT,
        OSPropertyKey.ATOM_CHIRAL_UNDEF_COUNT,
        OSPropertyKey.BOND_CHIRAL_COUNT,
        OSPropertyKey.BOND_CHIRAL_DEF_COUNT,
        OSPropertyKey.BOND_CHIRAL_UNDEF_COUNT,
        OSPropertyKey.CHARGE,
        OSPropertyKey.COVALENT_UNIT_COUNT,
        OSPropertyKey.HEAVY_ATOM_COUNT,
        OSPropertyKey.HYDROGEN_BOND_ACCEPTOR_COUNT,
        OSPropertyKey.HYDROGEN_BOND_DONOR_COUNT,
        OSPropertyKey.ISOTOPE_ATOM_COUNT,
        OSPropertyKey.ROTATABLE_BOND_COUNT,
        OSPropertyKey.TAUTOMERS_COUNT,
    ]

    def __init__(self):
        abs_filepath = os.path.join(ROOTDIR, self.PROPERTY_BOUNDS_FILEPATH)
        if not os.path.exists(abs_filepath):
            from locate_then_ask.kg_client import KgClient

            kg_client = KgClient(
                "http://178.128.105.213:3838/blazegraph/namespace/ontospecies/sparql"
            )

            query_template = """PREFIX os: <http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#>

SELECT DISTINCT (MIN(?Value) AS ?ValueMin) (MAX(?Value) AS ?ValueMax) WHERE {{
    ?x a os:{Prop} ; os:value ?Value .
}}"""
            prop2bounds: Dict[str, Tuple[float, float]] = dict()
            for prop in OSPropertyKey:
                query = query_template.format(Prop=prop.value)
                binding = kg_client.query(query)["results"]["bindings"][0]
                prop2bounds[prop.value] = (
                    binding["ValueMin"]["value"],
                    binding["ValueMax"]["value"],
                )

            os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
            with open(abs_filepath, "w") as f:
                json.dump(prop2bounds, f, indent=4)
        else:
            with open(abs_filepath, "r") as f:
                prop2bounds = json.load(f)

        self.prop2bounds = {
            OSPropertyKey(key): value for key, value in prop2bounds.items()
        }

    def _make(self, key: OSPropertyKey, low: float, high: float):
        fn = random.randint if key in self.INT_PROPERTIES else random.randrange
        return fn(low, high)

    def make(self):
        return {
            key: self._make(key, low, high)
            for key, (low, high) in self.prop2bounds.items()
        }


class OSIdentifierSynthesizer:
    IDENTIFIERS_FILEPATH = "data/ontospecies/Identifiers.json"
    IDENTIFIERS_NUM = 3

    def __init__(self):
        abs_filepath = os.path.join(ROOTDIR, self.IDENTIFIERS_FILEPATH)
        if not os.path.exists(abs_filepath):
            from locate_then_ask.kg_client import KgClient

            kg_client = KgClient(
                "http://178.128.105.213:3838/blazegraph/namespace/ontospecies/sparql"
            )

            query_template = """PREFIX os: <http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#>

SELECT DISTINCT ?Value WHERE {{
    ?x a os:{Ident} ; os:value ?Value .
}}
LIMIT 100"""

            identifier2values = dict()
            for key in OSIdentifierKey:
                query = query_template.format(Ident=key.value)
                bindings = kg_client.query(query)["results"]["bindings"]
                identifier2values[key.value] = [
                    binding["Value"]["value"] for binding in bindings
                ]

            os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
            with open(abs_filepath, "w") as f:
                json.dump(identifier2values, f, indent=4)
        else:
            with open(abs_filepath, "r") as f:
                identifier2values = json.load(f)

        self.identifier2values = {
            OSIdentifierKey(key): value for key, value in identifier2values.items()
        }

    def make(self):
        return {
            key: random.sample(value, min(self.IDENTIFIERS_NUM, len(value)))
            for key, value in self.identifier2values.items()
        }


class OSSpeciesSynthesizer:
    def __init__(self):
        self.prop_synth = OSPropertySynthesizer()
        self.ident_synth = OSIdentifierSynthesizer()

    def make(self):
        return OSSpecies(
            iri="synthetic_entity",
            key2identifier=self.prop_synth.make(),
            key2property=self.ident_synth.make(),
            chemclasses=None,
            uses=None,
        )
