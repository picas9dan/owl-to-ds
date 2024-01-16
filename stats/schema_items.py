import argparse
from collections import defaultdict
import json
from typing import Iterable

import networkx as nx

from locate_then_ask.query_graph import QueryGraph
from utils.json import as_enum


def count_schema_items(query_graphs: Iterable[QueryGraph]):
    prop2freq = defaultdict(lambda: 0)
    cls2freq = defaultdict(lambda: 0)

    for query_graph in query_graphs:
        for s, o, p in query_graph.edges(data="label"):
            props = p.split("/")
            if props[-1] in ["a", "rdfs:subClassOf", "rdfs:subClassOf*"]:
                cls2freq[o] += 1
            if props[0] in ["rdfs:subClassOf", "rdfs:subClassOf*"]:
                cls2freq[s] += 1
            for prop in props:
                if prop.startswith("^"):
                    prop = prop[1:]
                prop2freq[prop] += 1

    return {
        "property": prop2freq,
        "class": cls2freq
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f, object_hook=as_enum)

    stats = count_schema_items(nx.node_link_graph(datum["query"]["graph"]) for datum in data)
    
    filename = args.input.rsplit(".", maxsplit=1)[0]
    with open(filename + "_stats_schema.json", "w") as f:
        json.dump(stats, f, indent=4)