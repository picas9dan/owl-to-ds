import random

from constants.ontobuiltenv import OBEAttrKey
from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBEAddressLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        """Locates the topic entity in the query_graph by its address.
        The query_graph is modified in-place."""
        assert entity.address is not None

        address_node = query_graph.make_blank_node(key=OBEAttrKey.ADDRESS)
        query_graph.add_triple("Property", "obe:hasAddress", address_node)

        sampling_frame = []
        if entity.address.postal_code is not None:
            sampling_frame.append("postal_code")
        if entity.address.street is not None:
            assert entity.address.street_number is not None
            sampling_frame.append("street_addr")
        assert len(sampling_frame) > 0

        sampled = random.choice(sampling_frame)
        if sampled == "postal_code":
            assert entity.address.postal_code is not None

            postalcode_node = query_graph.make_literal_node(entity.address.postal_code)
            query_graph.add_triple(address_node, "obe:hasPostalCode/rdfs:label", postalcode_node)

            verbn = "the postal code [{code}]".format(code=entity.address.postal_code)
        elif sampled == "street_addr":
            assert entity.address.street is not None
            assert entity.address.street_number is not None

            street_node = query_graph.make_literal_node(entity.address.street)
            streetnum_node = query_graph.make_literal_node(entity.address.street_number)
            query_graph.add_triples([
                (address_node, "ict:hasStreetNumber", streetnum_node),
                (address_node, "ict:hasStreet", street_node)
            ])

            verbn = "[{number} {street}]".format(
                number=entity.address.street_number, street=entity.address.street
            )

        verbn = "addresss is at " + verbn

        return verbn
