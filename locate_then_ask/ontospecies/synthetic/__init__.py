from locate_then_ask.ontospecies.model import OSSpecies
from .property import OSPropertySynthesizer
from .identifier import OSIdentifierSynthesizer


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
