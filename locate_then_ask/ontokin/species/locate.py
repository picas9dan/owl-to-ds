import random
from locate_then_ask.ontokin.entity_store import OKEntityStore
from locate_then_ask.ontokin.model import OKSpecies
from locate_then_ask.query_graph import QueryGraph


class OKSpeciesLocator:
    def __init__(self, store: OKEntityStore):
        self.store = store

    def locate_entity_name(self, entity_iri: str):
        entity = self.store.get(entity_iri)
        assert isinstance(entity, OKSpecies)

        label = entity.label

        query_graph = QueryGraph()
        query_graph.add_node(
            "Species",
            iri=entity_iri,
            rdf_type="os:Species",
            label=label,
            template_node=True,
            topic_entity=True,
        )

        verbalization = "[{entity}]".format(entity=label)

        return query_graph, verbalization

    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_node(
            "Species",
            iri=entity_iri,
            rdf_type="os:Species",
            topic_entity=True,
        )
        return query_graph, "the chemical species"

    def locate_concept_and_relation(self, entity_iri: str):
        query_graph, verbalization = self.locate_concept_name(entity_iri)
        entity = self.store.get(entity_iri)
        assert isinstance(entity, OKSpecies)

        mechanism_iri = random.choice(entity.mechanism_iris)
        mechanism = self.store.get(mechanism_iri)
        query_graph.add_nodes_from(
            [
                (
                    "Mechanism",
                    dict(iri=mechanism.iri, rdf_type="okin:ReactionMechanism"),
                ),
                (
                    "Literal",
                    dict(label=mechanism.doi, template_node=True, literal=True),
                ),
            ]
        )
        query_graph.add_edges_from(
            [
                (
                    "Species",
                    "Mechanism",
                    dict(label="okin:belongsToPhase/^okin:hasGasPhase"),
                ),
                ("Mechanism", "Literal", dict(label="okin:hasProvenance/oprvn:hasDOI")),
            ]
        )

        verbalization += (
            " that appears in the reaction mechanism found in [{label}]".format(
                label=mechanism.doi
            )
        )

        return query_graph, verbalization
