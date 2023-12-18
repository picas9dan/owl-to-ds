
import copy
import random

from locate_then_ask.ontobuiltenv.locate.attr import OBEAttrLocator
from locate_then_ask.ontobuiltenv.model import OBEProperty
from locate_then_ask.query_graph import QueryGraph


class OBEAddressLocator(OBEAttrLocator):
    def locate(self, query_graph: QueryGraph, entity: OBEProperty):
        assert entity.address is not None

        query_graph = copy.deepcopy(query_graph)

        bn = query_graph.make_blank_node()
        query_graph.add_edge("Property", bn, label="obe:hasAddress")

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
            query_graph.add_edge(
                bn, postalcode_node, label="obe:hasPostalCode/rdfs:label"
            )

            verbn = "the postal code [{code}]".format(code=entity.address.postal_code)
        elif sampled == "street_addr":
            assert entity.address.street is not None
            assert entity.address.street_number is not None

            street_node = query_graph.make_literal_node(entity.address.street)
            streetnum_node = query_graph.make_literal_node(entity.address.street_number)
            query_graph.add_edges_from(
                [
                    (bn, streetnum_node, dict(label="ict:hasStreetNumber")),
                    (bn, street_node, dict(label="ict:hasStreet")),
                ]
            )

            verbn = "[{number} {street}]".format(
                number=entity.address.street_number, street=entity.address.street
            )

        verbn = "addresss is at " + verbn

        return query_graph, verbn
