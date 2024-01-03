import random
from typing import Iterable

from constants.functions import NumOp, StrOp
from constants.ontospecies import (
    OSIdentifierKey,
    OSPropertyKey,
    OSSpeciesAttrKey,
)
from locate_then_ask.ontospecies.entity_store import OSEntityStore
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


class OSSpeciesLocator:
    IDENTIFIER_WHITELIST = [
        OSIdentifierKey.INCHI,
        OSIdentifierKey.IUPAC_NAME,
        OSIdentifierKey.MOLECULAR_FORMULA,
        OSIdentifierKey.SMILES
    ]

    def __init__(self):
        self.store = OSEntityStore()

    def locate_entity_name(self, entity_iris: Iterable[str]):
        entity_names = []
        for entity_iri in entity_iris:
            entity = self.store.get(entity_iri)
            identifier_keys = [
                x for x in self.IDENTIFIER_WHITELIST if x.value in entity.key2identifier
            ]
            identifier_key = random.choice(identifier_keys)
            entity_name = random.choice(entity.key2identifier[identifier_key.value])
            entity_names.append(entity_name)

        query_graph = QueryGraph()
        query_graph.add_topic_node("Species", iri=entity_iris)
        query_graph.add_func("Species", operator=StrOp.VALUES, operand=entity_names)

        verbalization = " and ".join(
            ["<entity>{entity}</entity>".format(entity=name) for name in entity_names]
        )
        return query_graph, verbalization

    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_topic_node("Species", iri=entity_iri)
        return query_graph, "chemical species"

    def locate_concept_and_literal_multi(self, entity_iri: str, cond_num: int = 2):
        query_graph, concept = self.locate_concept_name(entity_iri)
        entity = self.store.get(entity_iri)

        keys = [
            OSSpeciesAttrKey.PROPERTY,
            OSSpeciesAttrKey.CHEMCLASS,
            OSSpeciesAttrKey.USE,
        ]

        counts_ontology = [x * 3 for x in [len(OSPropertyKey), 1, 1]]
        counts_entity = [
            len(entity.key2property),
            len(entity.chemclasses),
            len(entity.uses),
        ]
        counts = [min(x, y) for x, y in zip(counts_ontology, counts_entity)]

        key2freq = dict()
        for k in random.sample(keys, counts=counts, k=cond_num):
            if k not in key2freq:
                key2freq[k] = 1
            else:
                key2freq[k] += 1

        verbns = []
        random.shuffle(key2freq)
        for key, freq in key2freq.items():
            if key is OSSpeciesAttrKey.PROPERTY:
                property_keys = random.sample(entity.key2property, k=freq)
                for k in property_keys:
                    query_graph.add_literal_node(k, key=key)
                    query_graph.add_triple("Species", "os:has" + k, k)

                    prop = random.choice(entity.key2property[k])
                    operator = random.choice(tuple(NumOp))
                    operand, verbn = make_operand_and_verbn(
                        operator, value=prop.value, to_int=random.getrandbits(1)
                    )

                    query_graph.add_func(k, operator=operator, operand=operand)
                    verbns.append(verbn)
            elif key is OSSpeciesAttrKey.CHEMCLASS:
                chemclasses = random.sample(entity.chemclasses, k=freq)
                for cc in chemclasses:
                    literal_node = query_graph.make_literal_node(value=cc, key=key)
                    query_graph.add_triple(
                        "Species", "os:hasChemicalClass/rdfs:label", literal_node
                    )

                template = "chemical class{suffix} {be} {chemclasses}"
                is_plural = freq > 1
                verbn = template.format(
                    suffix="es" if is_plural else "",
                    be="are" if is_plural else "is",
                    chemclasses=" and ".join(chemclasses),
                )
                verbns.append(verbn)
            elif key is OSSpeciesAttrKey.USE:
                uses = random.sample(entity.uses, k=freq)
                for use in uses:
                    literal_node = query_graph.make_literal_node(value=use, key=key)
                    query_graph.add_triple(
                        "Species", "os:hasUse/rdfs:label", literal_node
                    )

                template = "use{suffix} {be} {uses}"
                is_plural = freq > 1
                verbn = template.format(
                    suffix="s" if is_plural else "",
                    be="are" if is_plural else "is",
                    uses=" and ".join(uses),
                )
            else:
                raise Exception("Unexpected key: " + key)

        verbalization = "the {concept} whose {conds}".format(
            concept=concept, conds=" and ".join(verbns)
        )

        return query_graph, verbalization
