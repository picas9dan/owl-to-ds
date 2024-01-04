from collections import defaultdict
import random

from locate_then_ask.ontokin.entity_store import OKEntityStore
from locate_then_ask.ontokin.model import (
    OKGasPhaseReaction,
    OKMechanism,
    OKSpecies,
)
from locate_then_ask.query_graph import QueryGraph


class OKReactionLocator:
    def __init__(self, store: OKEntityStore):
        self.store = store

    def locate_concept_and_attribute(self, entity_iri: str):
        entity = self.store.get(entity_iri)
        assert isinstance(entity, OKGasPhaseReaction)

        eqn = random.choice(entity.equations)

        query_graph = QueryGraph()
        eqn_node = query_graph.make_literal_node(eqn)
        query_graph.add_topic_node("Reaction", iri=entity_iri)
        query_graph.add_triple("Reaction", "okin:hasEquation", eqn_node)

        verbalization = "the chemical reaction [{entity}]".format(entity=eqn)

        if random.getrandbits(1):
            mechanism_iri = random.choice(entity.mechanism_iris)
            mechanism = self.store.get(mechanism_iri)
            assert isinstance(mechanism, OKMechanism)

            mechanism_node = "Mechanism"
            doi_node = query_graph.make_literal_node(mechanism.doi)
            query_graph.add_node(mechanism_node, iri=mechanism.iri)
            query_graph.add_triples(
                [
                    ("Reaction", "^okin:hasReaction", mechanism_node),
                    (mechanism_node, "okin:hasProvenance/op:hasDOI", doi_node),
                ]
            )

            verbalization += " involved in the mechanism {verb} in [{label}]".format(
                verb=random.choice(
                    ["found", "proposed", "outlined", "indicated", "shown"]
                ),
                label=mechanism.doi,
            )

        return query_graph, verbalization

    def locate_concept_and_relation_multi(self, entity_iri: str, cond_num: int):
        verbalized_conds = []
        query_graph = QueryGraph()
        query_graph.add_topic_node("Reaction", iri=entity_iri)
        entity = self.store.get(entity_iri)
        assert isinstance(entity, OKGasPhaseReaction)

        popln = ["reactant", "product", "mechanism"]
        counts = [len(entity.reactant_iris), len(entity.product_iris), 1]
        keys = random.sample(popln, counts=counts, k=min(cond_num, sum(counts)))

        key2freq = defaultdict(lambda: 0)
        for k in keys:
            key2freq[k] += 1

        if random.getrandbits(1):
            key2freq["participant"] = key2freq["reactant"] + key2freq["product"]
            del key2freq["reactant"]
            del key2freq["product"]

        random.shuffle(popln)
        for key in popln:
            freq = key2freq[key]
            if freq == 0:
                continue

            if key == "reactant":
                labels = []
                for reactant_iri in random.sample(entity.reactant_iris, k=freq):
                    reactant = self.store.get(reactant_iri)
                    assert isinstance(reactant, OKSpecies)

                    literal_node = query_graph.make_literal_node(reactant.label)
                    query_graph.add_triple(
                        "Reaction", "ocape:hasReactant/skos:altLabel", literal_node
                    )
                    labels.append(reactant.label)

                template = random.choice(
                    ["has reactants {values}", "consumes {values}"]
                )
                verbalized_conds.append(
                    template.format(values=" and ".join(["[{x}]" for x in labels]))
                )
            elif key == "product":
                labels = []
                for product_iri in random.sample(entity.product_iris, k=freq):
                    product = self.store.get(product_iri)
                    assert isinstance(product, OKSpecies)

                    literal_node = query_graph.make_literal_node(product.label)
                    query_graph.add_triple(
                        "Reaction", "ocape:hasProduct/skos:altLabel", literal_node
                    )
                    labels.append(product.label)

                template = random.choice(["has products {values}", "produces {values}"])
                verbalized_conds.append(
                    template.format(values=" and ".join(["[{x}]" for x in labels]))
                )
            elif key == "participant":
                labels = []
                for species_iri in random.sample(
                    entity.reactant_iris + entity.product_iris, k=freq
                ):
                    species = self.store.get(species_iri)
                    assert isinstance(species, OKSpecies)

                    literal_node = query_graph.make_literal_node(species.label)
                    query_graph.add_triple(
                        "Reaction",
                        "(ocape:hasReactant|ocape:hasProduct)/skos:altLabel",
                        literal_node,
                    )
                    labels.append(species.label)

                template = "{V} [{values}]"
                verbalized_conds.append(
                    template.format(
                        V=random.choice(
                            ["has", "features", "includes", "is participated by"]
                        ),
                        values=" and ".join(["[{x}]" for x in labels]),
                    )
                )
            elif key == "mechanism":
                assert freq == 1
                mechanism_iri = random.choice(entity.mechanism_iris)
                mechanism = self.store.get(mechanism_iri)

                literal_node = query_graph.make_literal_node(mechanism.doi)
                query_graph.add_node("Mechanism", iri=mechanism_iri)
                query_graph.add_triples(
                    [
                        ("Reaction", "^okin:hasReaction", "Mechanism"),
                        ("Mechanism", "okin:hasProvenance/op:hasDOI", literal_node),
                    ]
                )

                template = "involved in the mechanism {verb} in [{label}]"
                verbalized_conds.append(
                    template.format(
                        verb=random.choice(
                            ["found", "proposed", "outlined", "indicated", "shown"]
                        ),
                        label=mechanism.doi,
                    )
                )
            else:
                raise Exception("Unexpected key: " + key)

        verbalization = "the chemical reaction that {conds}".format(
            conds=" and ".join(verbalized_conds)
        )

        return query_graph, verbalization
