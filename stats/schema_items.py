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
            if p in ["a", 'a/rdfs:subClassOf', "a/rdfs:subClassOf*"] or p.endswith("/a"):
                cls2freq[o] += 1
            elif p in ["rdfs:subClassOf", "rdfs:subClassOf*"]:
                cls2freq[s] += 1
                cls2freq[o] += 1
            else:
                for _p in p.split("/"):
                    if _p.startswith("^"):
                        _p = _p[1:]
                    prop2freq[_p] += 1

    return {
        "property": prop2freq,
        "class": cls2freq
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f, object_hook=as_enum)

    stats = count_schema_items(nx.node_link_graph(datum["query"]["graph"]) for datum in data)

    with open(args.output, "w") as f:
        json.dump(stats, f, indent=4)