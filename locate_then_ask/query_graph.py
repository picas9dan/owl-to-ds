from decimal import Decimal
from typing import Optional, Union
import networkx as nx

class QueryGraph(nx.DiGraph):
    _LITERAL_PREFIX = "Literal_"
    _BN_PREFIX = "BN_"

    @classmethod
    def is_literal_node(cls, n: str):
        return n.startswith(cls._LITERAL_PREFIX)

    @classmethod
    def is_blank_node(cls, n: str):
        return n.startswith(cls._BN_PREFIX)

    def get_preds(self, subj: str):
        return [p for u, _, p in self.edges(data="label") if u == subj]

    def get_objs(self, subj: str, predicate: str):
        return [
            v
            for u, v, label in self.edges(data="label")
            if u == subj and label == predicate
        ]

    def make_literal_node(self, value: Optional[Union[str, Decimal]] = None):
        """Adds a literal node to the graph and returns the node."""
        literal_num = sum(n.startswith(self._LITERAL_PREFIX) for n in self.nodes())
        n = self._LITERAL_PREFIX + str(literal_num)

        self.add_node(n, literal=True, template_node=value is not None, label=value)

        return n

    def make_blank_node(self):
        """Adds a blank node to the graph and returns the node."""
        bn_num = sum(n.startswith(self._BN_PREFIX) for n in self.nodes())
        n = self._BN_PREFIX + str(bn_num)

        self.add_node(n, blank_node=True)

        return n