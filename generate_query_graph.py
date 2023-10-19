import random
from typing import Iterable, List, Optional

from SPARQLWrapper import JSON, POST, SPARQLWrapper
import networkx as nx
from constants import QUERY_PREFIXES, RDF_TYPE

from utils import Utils


class QueryGraphGenerator:
    def __init__(
        self,
        ontology: nx.DiGraph,
        numerical_classes: List[str] = [],
        prop_blacklist: List[str] = [],
        questionnode_blacklist: List[str] = [],
        kg_endpoint: str = "http://178.128.105.213:3838/blazegraph/namespace/ontospecies/sparql",
    ):
        G = Utils.flatten_subclassof(ontology)
        G = Utils.remove_egdes_by_label(G, labels=prop_blacklist)
        self.ontology = G
        self.numerical_classes = numerical_classes
        self.questionnode_blacklist = questionnode_blacklist

        sparql_client = SPARQLWrapper(kg_endpoint)
        sparql_client.setReturnFormat(JSON)
        sparql_client.setMethod(POST)
        self.sparql_client = sparql_client

    def generate_queryTemplate(
        self,
        edge_num: int,
        question_node: Optional[str] = None,
    ):
        if question_node is None:
            sampling_frame = [
                n for n in self.ontology.nodes() if n not in self.questionnode_blacklist
            ]
            question_node = random.choices(
                sampling_frame,
                weights=[self.ontology.degree[n] for n in sampling_frame],
            )[0]

        G = nx.MultiDiGraph()
        G.add_node(question_node, question_node=True)
        for _ in range(edge_num):
            n = random.choices(
                list(G.nodes()),
                weights=[int(self.ontology.degree[n] > 0) for n in G.nodes()],
            )[0]

            out_edges = list(self.ontology.out_edges(n, data="label"))
            in_edges = list(self.ontology.in_edges(n, data="label"))

            edge = random.choice(out_edges + in_edges)
            G.add_edge(edge[0], edge[1], label=edge[2])

        for n, question_node in G.nodes(data="question_node"):
            if question_node:
                continue
            if random.uniform(0, 1) < 0.8:
                G.nodes[n]["template_node"] = True
                if n in self.numerical_classes:
                    comparative = random.choice(["<", "<=", ">", ">=", "=", "≈"])
                    G.nodes[n]["function"] = comparative

        return G

    def query_kg(self, query: str):
        self.sparql_client.setQuery(query)
        return self.sparql_client.queryAndConvert()

    def cls2var(self, cls: str):
        cls = Utils.shortenIri(cls)
        return f"{cls.split(':', maxsplit=1)[-1]}"

    def make_query(
        self,
        triples: Iterable[str],
        result_vars: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ):
        triples = "\n  ".join(triples)
        select_vars = "\n  " + " ".join(result_vars) if result_vars is not None else "*"
        limit_clause = f"\nLIMIT {limit}" if limit is not None else ""
        return f"""{QUERY_PREFIXES}

SELECT {select_vars} WHERE {{{triples}
}}{limit_clause}"""

    def get_valueBinding_from_queryTemplate(self, query_template: nx.MultiDiGraph):
        triples = list()
        for h, t, prop in query_template.edges(data="label"):
            h, t, prop = (Utils.shortenIri(x) for x in (h, t, prop))
            h_var, t_var = (self.cls2var(x) for x in (h, t))
            triples.append(f"?{h_var} {prop} ?{t_var} .")
            if h != "rdfs:Literal":
                triples.append(f"?{h_var} a {h} .")
            if t != "rdfs:Literal":
                triples.append(f"?{t_var} a {t} .")
        query = self.make_query(triples)
        bindings = self.query_kg(query)["results"]["bindings"]

        if len(bindings) == 0:
            return None
        return bindings[0]

    def template2graph(self, query_template: nx.MultiDiGraph):
        binding = self.get_valueBinding_from_queryTemplate(query_template)
        if binding is None:
            return None
        
        def get_querygraph_entity(cls: str):
            if query_template.nodes[cls].get("template_node"):
                return binding[self.cls2var(cls)]["value"]
            return self.cls2var(cls)

        query_graph = nx.DiGraph()
        for node, attr in query_template.nodes(data=True):
            query_graph.add_node(get_querygraph_entity(node), **attr)
            if not attr.get("template_node"):
                query_graph.add_edge(get_querygraph_entity(node), node, label=RDF_TYPE)

        for h, t, attr in query_template.edges(data=True):
            query_graph.add_edge(
                get_querygraph_entity(h), get_querygraph_entity(t), **attr
            )

        return query_graph

    def minimize_queryGraph(self, query_graph: nx.DiGraph):
        return query_graph

    def generate_queryGraph(
        self, edge_num: int = 1, question_node: Optional[str] = None
    ):
        query_template = self.generate_queryTemplate(
            edge_num=edge_num, question_node=question_node
        )
        query_graph = self.template2graph(query_template)
        return query_graph, query_template
