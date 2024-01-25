import copy
import random
from typing import Iterable

from constants.functions import (
    COMPARATIVE_COND_MAKER,
    OSNumOp
)
from constants.ontospecies import CHEMCLASS_KEY, KEY2LABELS, USE_KEY
from locate_then_ask.ontospecies.entity_store import OSEntityStore
from locate_then_ask.query_graph import QueryGraph, get_objs, get_preds
from utils.numerical import get_gt, get_lt


class OSSpeciesLocator:
    IDENTIFIER_WHITELIST = [
        "InChI",
        "IUPACName",
        "MolecularFormula",
        "SMILES",
    ]

    def __init__(self):
        self.store = OSEntityStore()

    def locate_entity_name(self, entity_iris: Iterable[str]):
        entity_names = []
        for entity_iri in entity_iris:
            entity = self.store.get(entity_iri)
            identifier_keys = [
                x for x in self.IDENTIFIER_WHITELIST if x in entity.key2identifier
            ]
            identifier_key = random.choice(identifier_keys)
            entity_name = random.choice(entity.key2identifier[identifier_key])
            entity_names.append(entity_name)

        query_graph = QueryGraph()
        query_graph.add_node(
            "Species",
            iri=entity_iris,
            label=entity_names,
            template_node=True,
            topic_entity=True,
        )

        verbalization = " and ".join(
            ["<entity>{entity}</entity>".format(entity=name) for name in entity_names]
        )
        return query_graph, verbalization

    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_node(
            "Species",
            iri=entity_iri,
            rdf_type="os:Species",
            label="os:Species",
            topic_entity=True,
        )
        return query_graph, "chemical species"

    def _locate_concept_and_literal(self, query_graph: QueryGraph):
        query_graph = copy.deepcopy(query_graph)
        topic_node = next(
            n
            for n, topic_entity in query_graph.nodes(data="topic_entity")
            if topic_entity
        )
        entity_iri = query_graph.nodes[topic_node]["iri"]
        entity = self.store.get(entity_iri)

        sampled_keys = [
            x[len("os:has") :]
            for x in get_preds(query_graph, subj="Species")
            if x.startswith("os:has")
        ]
        unsampled_property_keys = [
            x for x in entity.key2property.keys() if x not in sampled_keys
        ]

        sampled_uses = get_objs(
            query_graph, subj="Species", predicate="os:hasUse/rdfs:label"
        )
        unsampled_uses = [x for x in entity.uses if x not in sampled_uses]

        sampled_chemclasses = get_objs(
            query_graph, subj="Species", predicate="os:hasChemicalClass/rdfs:label"
        )
        unsampled_chemclasses = [
            x for x in entity.chemclasses if x not in sampled_chemclasses
        ]

        sampling_frame = (
            unsampled_property_keys + unsampled_uses + unsampled_chemclasses
        )
        if len(sampling_frame) == 0:
            return query_graph, None

        new_sample = random.choice(sampling_frame)
        if new_sample in unsampled_property_keys:
            key = new_sample
            predicate = "os:has{PropertyName}/os:value".format(PropertyName=key)

            species_property = random.choice(entity.key2property[key])
            property_value = species_property.value
            operator = random.choice([x.value for x in OSNumOp])

            if operator in [OSNumOp.LESS_THAN, OSNumOp.LESS_THAN_EQUAL]:
                num_value = get_gt(property_value)
            elif operator in [OSNumOp.GREATER_THAN, OSNumOp.GREATER_THAN_EQUAL]:
                num_value = get_lt(property_value)
            elif operator in [OSNumOp.EQUAL, OSNumOp.AROUND]:
                num_value = property_value
            elif operator in [OSNumOp.INSIDE_RANGE, OSNumOp.OUTSIDE_RANGE]:
                num_value = (get_lt(property_value), get_gt(property_value))
            else:
                raise ValueError("Unrecognised comparative: " + operator)

            node = key + "Value"
            node_label = node
            template_node = False

            # qualifier_key = "reference state"
            # qualifier_value = species_property.reference_state_value
        elif new_sample in unsampled_chemclasses:
            key = CHEMCLASS_KEY
            predicate = "os:hasChemicalClass/rdfs:label"
            node_label = new_sample
            node = None
            operator = None
            template_node = True
            # qualifier_key = None
            # qualifier_value = None
        elif new_sample in unsampled_uses:
            key = USE_KEY
            predicate = "os:hasUse/rdfs:label"
            node_label = new_sample
            node = None
            operator = None
            template_node = True
            # qualifier_key = None
            # qualifier_value = None
        else:
            raise Exception("Unexpected sample: " + new_sample)

        key_label = random.choice(KEY2LABELS[key])

        if node is None:
            literal_num = len(
                [n for n in query_graph.nodes() if n.startswith("Literal_")]
            )
            node = "Literal_" + str(literal_num)

        query_graph.add_node(
            node, label=node_label, literal=True, template_node=template_node
        )
        query_graph.add_edge("Species", node, label=predicate)

        if operator is None:
            verbalization = "{K} is {V}".format(
                K=key_label, V="[{x}]".format(x=node_label)
            )
        else:
            cond = COMPARATIVE_COND_MAKER[operator](num_value)

            func_node = node + "_func"
            func_label = "{op}\n{val}".format(op=operator, val=num_value)
            query_graph.add_node(
                func_node,
                operator=operator,
                operand=num_value,
                label=func_label,
                func=True,
                template_node=True,
            )
            query_graph.add_edge(node, func_node, label="func")

            verbalization = "{K} is {COND}".format(K=key_label, COND=cond)

        # if (
        #     qualifier_key is not None
        #     and qualifier_value is not None
        #     and random.getrandbits(1)
        # ):
        #     query_graph.nodes[literal_node]["qualifier_key"] = qualifier_key
        #     query_graph.nodes[literal_node]["qualifier_value"] = qualifier_value

        #     qualifier_template = " ({QK} is {QV})"
        #     verbalization += qualifier_template.format(
        #         QK=qualifier_key, QV=qualifier_value
        #     )

        return query_graph, verbalization

    def locate_concept_and_literal_multi(self, entity_iri: str, cond_num: int = 2):
        verbalized_conds = []
        query_graph, concept = self.locate_concept_name(entity_iri)

        for _ in range(cond_num):
            query_graph, verbalized_cond = self._locate_concept_and_literal(query_graph)
            if verbalized_cond is not None:
                verbalized_conds.append(verbalized_cond)

        verbalization = "the {concept} whose {conds}".format(
            concept=concept, conds=" and ".join(verbalized_conds)
        )

        return query_graph, verbalization
