import copy
from decimal import Decimal
import random
from constants.functions import NumOp
from constants.namespaces import DABGEO, OBE, OM
from constants.om import OM_KEY_LABELS
from constants.ontobuiltenv import (
    OBE_ATTR_KEYS,
    OBE_ATTR_LABELS,
    OBE_PROPERTYUSAGE_LABELS,
    OBEAttrKey,
)
from locate_then_ask.ontobuiltenv.entity_store import OBEEntityStore
from locate_then_ask.ontobuiltenv.model import OmMeasure
from locate_then_ask.query_graph import QueryGraph
from utils.numerical import make_operand_and_verbn


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

        assert entity.built_form.startswith(OBE), entity.built_form
        clsname = entity.built_form[len(OBE) :]
        clsname_node = "obe:" + clsname
        query_graph.add_node(clsname_node, prefixed=True, template_node=True)
        query_graph.add_edge("Property", clsname_node, label="obe:hasBuiltForm/a")

        verbn = "built form is " + clsname

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

        operator = random.choice(tuple(NumOp))
        operand, verbn = make_operand_and_verbn(
            operator, value=entity.number_of_habitable_rooms, to_int=True
        )

        literal_node = "NumberOfHabitableRooms"
        func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
        func_node = "Func_" + str(func_num)
        func_label = operator.value + "\n" + str(operand)

        query_graph.add_nodes_from(
            [
                (literal_node, dict(literal=True)),
                (
                    func_node,
                    dict(
                        func=True,
                        template_node=True,
                        operator=operator,
                        operand=operand,
                        label=func_label,
                    ),
                ),
            ]
        )
        query_graph.add_edges_from(
            [
                ("Property", literal_node, dict(label="obe:hasNumberOfHabitableRooms")),
                (literal_node, func_node, dict(label="func")),
            ]
        )

        verbn = "number of habitable room is " + verbn

        return query_graph, verbn

    def _locate_propertyType(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.property_type is not None

        ns, propertytype_clsname = entity.property_type.rsplit("/", maxsplit=1)
        assert ns + "/" == OBE, ns
        propertytype_clsname_node = "obe:" + propertytype_clsname
        query_graph.add_node(
            propertytype_clsname_node, prefixed=True, template_node=True
        )
        query_graph.add_edge(
            "Property", propertytype_clsname_node, label="obe:hasPropertyType/a"
        )

        verbn = "property type is " + propertytype_clsname

        return query_graph, verbn

    def _locate_propertyUsage(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert any(entity.property_usage)

        verbns = []
        samples = random.sample(
            entity.property_usage,
            k=random.choice(range(1, len(entity.property_usage) + 1)),
        )
        for i, use in enumerate(samples):
            use_node = "PropertyUsage_" + str(i)
            assert use.concept.startswith(OBE), use.concept
            clsname = use.concept[len(OBE) :]
            clsname_node = "obe:" + clsname

            query_graph.add_nodes_from(
                [
                    (use_node, dict()),
                    (clsname_node, dict(template_node=True, prefixed=True)),
                ]
            )
            query_graph.add_edges_from(
                [
                    ("Property", use_node, dict(label="obe:hasPropertyUsage")),
                    (use_node, clsname_node, dict(label="a/rdfs:subClassOf*")),
                ]
            )

            verbn = random.choice(OBE_PROPERTYUSAGE_LABELS[clsname])

            if use.usage_share is not None:
                operator = random.choice(tuple(NumOp))
                share_pctg = use.usage_share * 100
                operand, verbn_numop = make_operand_and_verbn(
                    operator,
                    value=share_pctg,
                    min_val=share_pctg / 2,
                    max_val=(100 + share_pctg) / 2,
                )

                if operator == NumOp.EQUAL:
                    verbn_numop = str(operand)

                share_pctg_str = str(operand)
                if share_pctg_str.endswith("00"):
                    share_pctg_str = share_pctg_str[:-2]
                share_pctg_str += "%"
                verbn_numop = verbn_numop.replace(str(operand), share_pctg_str)
                operand = operand / 100

                literal_node = "UsageShare_" + str(i)
                func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
                func_node = "Func_" + str(func_num)
                func_label = operator.value + "\n" + str(operand)

                query_graph.add_nodes_from(
                    [
                        (literal_node, dict(template_node=True)),
                        (
                            func_node,
                            dict(
                                func=True,
                                template_node=True,
                                operator=operator,
                                operand=operand,
                                label=func_label,
                            ),
                        ),
                    ]
                )
                query_graph.add_edges_from(
                    [
                        (use_node, literal_node, dict(label="obe:hasUsageShare")),
                        (literal_node, func_node, dict(label="func")),
                    ]
                )
                verbn = verbn + " for " + verbn_numop

            verbns.append(verbn)

        verbalization = "use is " + " and ".join(verbns)

        return query_graph, verbalization

    def _locate_omMeasure(
        self, query_graph: QueryGraph, key: OBEAttrKey, measure: OmMeasure
    ):
        operator = random.choice(tuple(NumOp))
        operand, op_verbn = make_operand_and_verbn(
            operator, value=measure.numerical_value
        )

        attrval_node = key.value + "Value"
        numval_node = key.value + "NumericalValue"

        func_num = sum(n.startswith("Func_") for n in query_graph.nodes())
        func_node = "Func_" + str(func_num)
        func_label = operator.value + "\n" + str(operand)

        assert measure.unit_iri.startswith(OM), measure.unit_iri
        unit = measure.unit_iri[len(OM) :]
        unit_node = "om:" + unit
        unit_verbn = random.choice(OM_KEY_LABELS[unit])

        query_graph.add_nodes_from(
            [
                (attrval_node, dict()),
                (numval_node, dict(template_node=True)),
                (
                    func_node,
                    dict(
                        func=True,
                        template_node=True,
                        operator=operator,
                        operand=operand,
                        label=func_label,
                    ),
                ),
                (unit_node, dict(template_node=True)),
            ]
        )
        query_graph.add_edges_from(
            [
                (
                    "Property",
                    attrval_node,
                    dict(label="obe:has{key}/om:hasValue".format(key=key.value)),
                ),
                (attrval_node, numval_node, dict(label="om:hasNumericalValue")),
                (numval_node, func_node, dict(label="func")),
                (attrval_node, unit_node, dict(label="om:hasUnit")),
            ]
        )

        verbn = "{key} {op} {unit}".format(
            key=random.choice(OBE_ATTR_LABELS[key]), op=op_verbn, unit=unit_verbn
        )

        return query_graph, verbn

    def _locate_totalFloorArea(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.total_floor_area is not None
        return self._locate_omMeasure(
            query_graph,
            key=OBEAttrKey.TOTAL_FLOOR_AREA,
            measure=entity.total_floor_area,
        )

    def _locate_marketValue(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.market_value is not None
        return self._locate_omMeasure(
            query_graph,
            key=OBEAttrKey.MARKET_VALUE,
            measure=entity.market_value
        )
    
    def _locate_groundElevation(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)
        assert entity.ground_elevation is not None
        return self._locate_omMeasure(
            query_graph,
            key=OBEAttrKey.GROUND_ELEVATION,
            measure=entity.ground_elevation
        )

    def _locate_concept_and_literal(self, query_graph: QueryGraph):
        entity, query_graph = self._retrieveTopicEntity_cloneQueryGraph(query_graph)

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
