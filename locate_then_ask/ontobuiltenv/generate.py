import json
import os
import random
import time
from typing import List

import networkx as nx
from tqdm import tqdm
from constants.fs import ROOTDIR

from locate_then_ask.ontobuiltenv.ask import OBEAsker
from locate_then_ask.ontobuiltenv.locate import OBELocator
from utils.json import EnumEncoder


SEED_ENTITIES_FILEPATH = "data/seed_entities/ontobuiltenv.txt"


class OBEDatasetGenerator:
    LOCATE2ASK = {
        "concept_name": (["count"], [1]),
        "concept_and_literal": (["name", "count", "attribute"], [1, 1, 1]),
    }

    @classmethod
    def query_seed_entities(self):
        from locate_then_ask.kg_client import KgClient

        kg_client = KgClient(
            "http://165.232.172.16:3838/blazegraph/namespace/kingslynn/sparql"
        )

        query_template = """PREFIX dabgeo:	  <http://www.purl.org/oema/infrastructure/>
PREFIX obe:       <https://www.theworldavatar.com/kg/ontobuiltenv/>

SELECT DISTINCT ?x (COUNT(DISTINCT ?p) as ?degree) WHERE {{
    ?x a {cls} .
    ?x ?p ?o .
}}
GROUP BY ?x
ORDER BY DESC(?degree)
LIMIT {num}"""

        iris: List[str] = []

        for cls, num in [("obe:Property", 50), ("obe:Flat", 100), ("dabgeo:Building", 200)]:
            query = query_template.format(
                cls=cls, num=num
            )
            bindings = kg_client.query(query)["results"]["bindings"]
            iris.extend([x["x"]["value"] for x in bindings])

        return tuple(iris)

    @classmethod
    def retrieve_seed_entities(self):
        filepath = os.path.join(ROOTDIR, SEED_ENTITIES_FILEPATH)

        if not os.path.isfile(filepath):
            print("No seed entities found. Retrieving seed entities...")
            entities = self.query_seed_entities()
            with open(filepath, "w") as f:
                f.write("\n".join(entities))
            print("Retrieval done.")

        with open(filepath, "r") as f:
            seed_entities = [x.strip() for x in f.readlines()]

        return [x for x in seed_entities if x]

    def __init__(self):
        self.locator = OBELocator()
        self.asker = OBEAsker()

        self.seed_entities = self.retrieve_seed_entities()
        random.shuffle(self.seed_entities)

    def generate(self):
        examples = []

        for i, entity in enumerate(tqdm(self.seed_entities)):
            locate_strategy = random.choice(list(self.LOCATE2ASK.keys()))

            if locate_strategy == "concept_name":
                query_graph, verbn = self.locator.locate_concept_name(entity)
            elif locate_strategy == "concept_and_literal":
                cond_num = random.sample([1, 2, 3, 4, 5], counts=[1, 2, 3, 2, 1], k=1)[0]
                query_graph, verbn = self.locator.locate_concept_and_literal_multi(entity, cond_num=cond_num)
            else:
                raise ValueError("Unexpected locate strategy: " + locate_strategy)
            
            ask_strategies, counts = self.LOCATE2ASK[locate_strategy]
            ask_strategy = random.sample(ask_strategies, counts=counts, k=1)[0]

            if ask_strategy == "name":
                query_sparql, verbn = self.asker.ask_name(query_graph, verbn)
            elif ask_strategy == "count":
                query_sparql, verbn = self.asker.ask_count(query_graph, verbn)
            elif ask_strategy == "attribute":
                attr_num = random.sample([1, 2, 3], counts=[3, 2, 1], k=1)[0]
                query_sparql, verbn = self.asker.ask_attrs(query_graph, verbn, attr_num=attr_num)
            else:
                raise ValueError("Unexpected ask strategy: " + ask_strategy)
            
            example = dict(
                id=i,
                verbalization=verbn,
                query=dict(
                    sparql=query_sparql,
                    graph=nx.node_link_data(query_graph),
                ),
            )
            examples.append(example)

        return examples


if __name__ == "__main__":
    ds_gen = OBEDatasetGenerator()
    examples = ds_gen.generate()

    time_label = time.strftime("%Y-%m-%d_%H.%M.%S")
    filename = "data/ontobuiltenv_{timestamp}.json".format(timestamp=time_label)

    with open(os.path.join(ROOTDIR, filename), "w") as f:
        json.dump(examples, f, indent=4, cls=EnumEncoder)