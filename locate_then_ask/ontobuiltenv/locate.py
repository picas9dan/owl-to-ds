import copy
import random
from constants.namespaces import DABGEO, OBE
from constants.ontobuiltenv import OBE_ATTR_KEYS, OBEAttrKey
from locate_then_ask.ontobuiltenv.entity_store import OBEEntityStore
from locate_then_ask.query_graph import QueryGraph


class OBELocator:
    def __init__(self) -> None:
        self.store = OBEEntityStore()

    def locate_concept_name(self, entity_iri: str):
        query_graph = QueryGraph()
        query_graph.add_node("Property", iri=entity_iri)

        entity = self.store.get(entity_iri)
        entity_cls = random.choice(entity.concepts)
        if entity_cls == DABGEO + "Building":
            query_graph.add_node("dabgeo:Building", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "dabgeo:Building", label="a")

            verbalization = "building"
        elif entity_cls == OBE + "Flat":
            query_graph.add_node("obe:Flat", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "obe:Flat", label="a")

            verbalization = "flat"
        elif entity_cls == OBE + "Property":
            query_graph.add_node("obe:Property", template_node=True, prefixed=True)
            query_graph.add_edge("Property", "obe:Property", label="a/rdfs:subClassOf*")

            verbalization = "property"
        else:
            raise ValueError("Unexpeced type: " + entity_cls.__name__)

        return query_graph, verbalization

    def _retrieveTopicEntity_cloneQueryGraph(self, query_graph):
        iri = query_graph.nodes["Property"]["iri"]
        entity = self.store.get(iri)
        return entity, copy.deepcopy(query_graph)

    def _locate_addr(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.address is not None

        query_graph.add_node("Address")
        query_graph.add_edge("Property", "Address", label="obe:hasAddress")

        sampling_frame = []
        if entity.address.postal_code is not None:
            sampling_frame.append("postal_code")
        if entity.address.street is not None:
            assert entity.address.street_number is not None
            sampling_frame.append("street_addr")
        assert len(sampling_frame) > 0

        sampled = random.choice(sampling_frame)
        literal_num = sum(n.startswith("Literal_") for n in query_graph.nodes())
        if sampled == "postal_code":
            assert entity.address.postal_code is not None

            literal_node = "Literal_" + str(literal_num)
            query_graph.add_node(
                literal_node,
                literal=True,
                template_node=True,
                label=entity.address.postal_code,
            )
            query_graph.add_edge(
                "Address", literal_node, label="obe:hasPostalCode/rdfs:label"
            )

            verbn = "the postal code [{code}]".format(code=entity.address.postal_code)
        elif sampled == "street_addr":
            assert entity.address.street is not None
            assert entity.address.street_number is not None

            street_node = "Literal_" + str(literal_num)
            streetnum_node = "Literal_" + str(literal_num + 1)
            query_graph.add_nodes_from(
                [
                    (
                        streetnum_node,
                        dict(
                            literal=True,
                            template_node=True,
                            label=entity.address.street_number,
                        ),
                    ),
                    (
                        street_node,
                        dict(
                            literal=True,
                            template_node=True,
                            label=entity.address.street,
                        ),
                    ),
                ]
            )
            query_graph.add_edges_from(
                [
                    ("Address", streetnum_node, dict(label="ict:hasStreetNumber")),
                    ("Address", street_node, dict(label="ict:hasStreet")),
                ]
            )

            verbn = "[{number} {street}]".format(
                number=entity.address.street_number, street=entity.address.street
            )

        verbn = "addresss is at " + verbn

        return query_graph, verbn

    def _locate_builtForm(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.built_form is not None

        ns, builtform_clsname = entity.built_form.rsplit("/", maxsplit=1)
        assert ns + "/" == OBE, ns
        builtform_clsname_node = "obe:" + builtform_clsname
        query_graph.add_node(builtform_clsname_node, prefixed=True, template_node=True)
        query_graph.add_edge(
            "Property", builtform_clsname_node, label="obe:hasBuiltForm/a"
        )

        verbn = "built form is " + builtform_clsname

        return query_graph, verbn

    def _locate_energyRating(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.energy_rating is not None

        literal_num = sum(n.startswith("Literal_") for n in query_graph.nodes())
        literal_node = "Literal_" + str(literal_num)
        query_graph.add_node(
            literal_node, label=entity.energy_rating, template_node=True, literal=True
        )
        query_graph.add_edge("Property", literal_node, label="obe:hasEnergyRating")

        verbn = "energy rating is [{label}]".format(label=entity.energy_rating)

        return query_graph, verbn

    def _locate_numOfHabitableRooms(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.number_of_habitable_rooms is not None

        literal_num = sum(n.startswith("Literal_") for n in query_graph.nodes())
        literal_node = "Literal_" + str(literal_num)
        query_graph.add_node(
            literal_node, label=entity.number_of_habitable_rooms, template_node=True, literal=True
        )
        query_graph.add_edge("Property", literal_node, label="obe:hasNumberOfHabitableRooms")

        verbn = "number of habitable room is " + str(entity.number_of_habitable_rooms)

        return query_graph, verbn

    def _locate_propertyType(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.property_type is not None
        
        ns, propertytype_clsname = entity.property_type.rsplit("/", maxsplit=1)
        assert ns + "/" == OBE, ns
        propertytype_clsname_node = "obe:" + propertytype_clsname
        query_graph.add_node(propertytype_clsname_node, prefixed=True, template_node=True)
        query_graph.add_edge(
            "Property", propertytype_clsname_node, label="obe:hasPropertyType/a"
        )

        verbn = "property type is " + propertytype_clsname

        return query_graph, verbn

    def _locate_concept_and_literal(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph

        sampled_attrs = tuple(
            OBEAttrKey(pred[len("obe:has") :])
            for _, _, pred in query_graph.out_edges("Property", data="label")
            if pred.startswith("obe:has")
        )
        unsampled_attrs = tuple(
            x for x in entity.get_nonnone_keys() if x not in sampled_attrs
        )
        key = random.choice(unsampled_attrs)

        if key == OBEAttrKey.ADDRESS:
            query_graph, verbn = self._locate_addr(query_graph)

    def locate_concept_and_literal_multi(self, entity_iri: str, cond_num: int = 2):
        pass
