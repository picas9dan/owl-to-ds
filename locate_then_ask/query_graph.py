import networkx as nx

class QueryGraph(nx.DiGraph):
    def get_preds(self, subj: str):
        return [p for u, _, p in self.edges(data="label") if u == subj]

    def get_objs(self, subj: str, predicate: str):
        return [
            v
            for u, v, label in self.edges(data="label")
            if u == subj and label == predicate
        ]
