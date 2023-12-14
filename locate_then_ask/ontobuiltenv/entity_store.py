from typing import Dict

from locate_then_ask.kg_client import KgClient
from locate_then_ask.ontobuiltenv.model import (
    IctAddress,
    OBEProperty,
    OmMeasure,
)


class OBEEntityStore:
    def __init__(
        self,
        kg_endpoint: str = "http://165.232.172.16:3838/blazegraph/namespace/kingslynn/sparql",
    ):
        self.kg_client = KgClient(kg_endpoint)
        self.iri2entity: Dict[str, OBEProperty] = dict()

    def get(self, entity_iri: str):
        if entity_iri not in self.iri2entity:
            self.iri2entity[entity_iri] = self.create(entity_iri)
        return self.iri2entity[entity_iri]

    def create(self, entity_iri: str):
        concepts = self.retrieve_str_byPredicate(entity_iri, predicate="a/rdfs:subClassOf*")
        address = self.retrieve_address(entity_iri)
        built_form = self.retrieve_str_byPredicate(
            entity_iri, predicate="obe:hasBuiltForm/a"
        )
        energy_rating = self.retrieve_str_byPredicate(
            entity_iri, predicate="obe:hasEnergyRating"
        )
        number_of_habitable_rooms = self.retrieve_str_byPredicate(
            entity_iri, predicate="obe:hasNumberOfHabitableRooms"
        )
        property_type = self.retrieve_str_byPredicate(
            entity_iri, predicate="obe:hasPropertyType/a"
        )
        property_usage = self.retrieve_str_byPredicate(
            entity_iri, predicate="obe:hasPropertyUsage/a*/rdfs:label"
        )
        total_floor_area = self.retrieve_omMeasure_byPredicate(
            entity_iri, predicate="obe:hasTotalFloorArea/om:hasValue"
        )
        market_value = self.retrieve_omMeasure_byPredicate(
            entity_iri, predicate="obe:hasMarketValue/om:hasValue"
        )
        ground_elevation = self.retrieve_omMeasure_byPredicate(
            entity_iri, predicate="obe:hasGroundElevation/om:hasValue"
        )

        return OBEProperty(
            iri=entity_iri,
            concepts=concepts,
            address=address,
            built_form=built_form[0] if len(built_form) > 0 else None,
            energy_rating=energy_rating[0] if len(energy_rating) > 0 else None,
            number_of_habitable_rooms=int(number_of_habitable_rooms[0])
            if len(number_of_habitable_rooms) > 0
            else None,
            property_type=property_type[0] if len(property_type) > 0 else None,
            property_usage=property_usage,
            total_floor_area=total_floor_area,
            market_value=market_value,
            ground_elevation=ground_elevation,
        )

    def retrieve_address(self, entity_iri: str):
        query_template = """PREFIX ict: <http://ontology.eil.utoronto.ca/icontact.owl#>
PREFIX obe: <https://www.theworldavatar.com/kg/ontobuiltenv/>

SELECT DISTINCT * WHERE {{
    <{IRI}> obe:hasAddress ?Address .
    OPTIONAL {{ ?Address ict:hasStreet ?Street }}
    OPTIONAL {{ ?Address ict:hasStreetNumber ?StreetNumber }}
    OPTIONAL {{ ?Address obe:hasUnitName ?UnitName }}
    OPTIONAL {{ ?Address obe:hasPostalCode/rdfs:label ?PostalCode }}
}}
LIMIT 1"""
        query = query_template.format(IRI=entity_iri)
        response_bindings = self.kg_client.query(query)["results"]["bindings"]

        if len(response_bindings) == 0:
            return None

        value_binding = {k: v["value"] for k, v in response_bindings[0].items()}
        return IctAddress(
            street=value_binding.get("Street"),
            street_number=value_binding.get("StreetNumber"),
            unit_name=value_binding.get("UnitName"),
            postal_code=value_binding.get("PostalCode"),
        )

    def retrieve_str_byPredicate(self, entity_iri: str, predicate: str):
        query_template = """PREFIX obe: <https://www.theworldavatar.com/kg/ontobuiltenv/>

SELECT DISTINCT ?o WHERE {{
    <{IRI}> {pred} ?o .
}}
LIMIT 1"""
        query = query_template.format(IRI=entity_iri, pred=predicate)

        response_bindings = self.kg_client.query(query)["results"]["bindings"]
        return [x["o"]["value"] for x in response_bindings]

    def retrieve_omMeasure_byPredicate(self, entity_iri: str, predicate: str):
        query_template = """PREFIX om: <http://www.ontology-of-units-of-measure.org/resource/om-2/>
PREFIX obe: <https://www.theworldavatar.com/kg/ontobuiltenv/>

SELECT DISTINCT * WHERE {{
    <{IRI}> {pred} [
        om:hasNumericalValue ?NumericalValue ;
        om:hasUnit ?Unit
    ] .
}}
LIMIT 1"""
        query = query_template.format(IRI=entity_iri, pred=predicate)

        response_bindings = self.kg_client.query(query)["results"]["bindings"]
        if len(response_bindings) == 0:
            return None
        return OmMeasure(
            numerical_value=response_bindings[0]["NumericalValue"]["value"],
            unit_iri=response_bindings[0]["Unit"]["value"],
        )
