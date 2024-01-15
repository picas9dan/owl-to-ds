import json
import os
import random
import time

import networkx as nx
from tqdm import tqdm
from constants.fs import ROOTDIR
from constants.ontospecies import OSPropertyKey

from locate_then_ask.query_graph import QueryGraph
from utils.json import EnumEncoder
from .ask import OSAsker
from .locate import OSSpeciesLocator
from .model import OSSpecies




class DatasetGenerator:
    def __init__(self):
        self.locator = OSSpeciesLocator()
        self.asker = OSAsker()

        self.seed_species = []
        random.shuffle(self.seed_species)

    def locate(self, locate_strategy: str, species_id: int):
        if locate_strategy == "entity_name":
            entity_num = min(
                random.sample(population=[1, 2, 3], counts=[16, 4, 1], k=1)[0],
                len(self.seed_species) - species_id,
            )
            entity_iris = self.seed_species[species_id : species_id + entity_num]

            query_graph, verbalization = self.locator.locate_entity_name(entity_iris)
            species_id_new = species_id + entity_num
        elif locate_strategy == "concept_and_literal":
            entity_iri = self.seed_species[species_id]
            cond_num = random.sample(
                population=[1, 2, 3, 4, 5], counts=[4, 8, 4, 2, 1], k=1
            )[0]

            query_graph, verbalization = self.locator.locate_concept_and_literal_multi(
                entity_iri, cond_num=cond_num
            )
            species_id_new = species_id + 1
        else:
            raise ValueError("Unrecognized locate strategy: " + locate_strategy)

        return query_graph, verbalization, species_id_new

    def ask(self, ask_strategy: str, query_graph: QueryGraph, verbalization: str):
        if ask_strategy == "name":
            return self.asker.ask_name(query_graph, verbalization)
        elif ask_strategy == "attribute":
            attr_num = random.sample(population=[1, 2, 3], counts=[16, 4, 1], k=1)[0]
            return self.asker.ask_attribute(
                query_graph=query_graph, verbalization=verbalization, attr_num=attr_num
            )
        else:
            raise ValueError("Unrecognized ask_strategy: " + ask_strategy)

    def generate(self):
        species_id = 0

        examples = []
        example_id = 0

        with tqdm(total=len(self.seed_species)) as pbar:
            while species_id < len(self.seed_species):
                locate_strategy = random.choice(list(self.LOCATE2ASK.keys()))
                query_graph, verbalization, species_id_new = self.locate(
                    locate_strategy=locate_strategy, species_id=species_id
                )

                if query_graph is None:
                    print(
                        "Unable to locate a subgraph with the following entity: "
                        + str(self.seed_species[species_id:species_id_new])
                    )
                    continue

                ask_strategy_population, ask_strategy_counts = self.LOCATE2ASK[
                    locate_strategy
                ]
                ask_strategy = random.sample(
                    population=ask_strategy_population, counts=ask_strategy_counts, k=1
                )[0]
                query_sparql, verbalization = self.ask(
                    ask_strategy=ask_strategy,
                    query_graph=query_graph,
                    verbalization=verbalization,
                )

                example = dict(
                    id=example_id,
                    verbalization=verbalization,
                    query=dict(
                        sparql=query_sparql,
                        graph=nx.node_link_data(query_graph),
                    ),
                )
                examples.append(example)
                example_id += 1

                pbar.update(species_id_new - species_id)
                species_id = species_id_new

        return examples


if __name__ == "__main__":
    ds_gen = DatasetGenerator()
    examples = ds_gen.generate()

    time_label = time.strftime("%Y-%m-%d_%H.%M.%S")
    filename = "data/ontospecies_{timestamp}.json".format(timestamp=time_label)

    with open(os.path.join(ROOTDIR, filename), "w") as f:
        json.dump(examples, f, indent=4, cls=EnumEncoder)
