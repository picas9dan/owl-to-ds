from decimal import Decimal
from typing import Any, Iterable, Optional, Tuple, Union
import networkx as nx

from constants.functions import NumOp, StrOp


class QueryGraph(nx.DiGraph):
    _LITERAL_PREFIX = "Literal_"
    _BN_PREFIX = "BN_"
    _FUNC_PREFIX = "Func_"
    _TOPICNODE_ATTRNAME = "topic_node"

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

    def add_topic_node(self, n: str, iri: str):
        self.add_node(n, topic_entity=True, iri=iri)

    def make_literal_node(self, value: Union[str, Decimal], key: Optional[Any] = None):
        """Adds a grounded literal node to the graph and returns the node."""
        literal_num = sum(n.startswith(self._LITERAL_PREFIX) for n in self.nodes())
        n = self._LITERAL_PREFIX + str(literal_num)

        self.add_node(n, literal=True, template_node=True, label=value, key=key)

        return n

    def add_literal_node(self, n: str, key: Optional[Any] = None):
        self.add_node(n, literal=True, key=key)

    def make_blank_node(self, key: Optional[Any] = None):
        """Adds a blank node to the graph and returns the node."""
        bn_num = sum(n.startswith(self._BN_PREFIX) for n in self.nodes())
        n = self._BN_PREFIX + str(bn_num)

        self.add_node(n, blank_node=True, key=key)

        return n

    def add_iri_node(self, iri: str, prefixed: bool, key: Optional[Any] = None):
        self.add_node(iri, iri=iri, template_node=True, prefixed=prefixed, key=key)

    def add_func(self, target_node: str, operator: Union[NumOp, StrOp], operand: Any):
        func_num = sum(n.startswith(self._FUNC_PREFIX) for n in self.nodes())
        func_node = self._FUNC_PREFIX + str(func_num)
        func_label = operator.value + "\n" + str(operand)

        self.add_node(
            func_node,
            func=True,
            template_node=True,
            operator=operator,
            operand=operand,
            label=func_label,
        )
        self.add_edge(target_node, func_node, label="func")

    def add_question_node(self, n: str, count: bool = False):
        self.add_node(n, question_node=True, count=count)

    def add_triple(self, s: str, p: str, o: str):
        self.add_edge(s, o, label=p)

    def add_triples(self, triples: Iterable[Tuple[str, str, str]]):
        self.add_edges_from([(s, o, dict(label=p)) for s, p, o in triples])
