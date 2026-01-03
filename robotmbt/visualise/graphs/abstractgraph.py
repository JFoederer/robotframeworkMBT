from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
import networkx as nx


NodeInfo = TypeVar('NodeInfo')
EdgeInfo = TypeVar('EdgeInfo')


class AbstractGraph(ABC, Generic[NodeInfo, EdgeInfo]):
    def __init__(self, info: TraceInfo):
        # The underlying storage - a NetworkX DiGraph
        self.networkx: nx.DiGraph = nx.DiGraph()

        # Keep track of node IDs
        self.ids: dict[str, NodeInfo] = {}

        # Add the start node
        self.networkx.add_node('start', label='start')
        self.start_node = 'start'

        # Add nodes and edges for all traces
        for trace in info.all_traces:
            for i in range(len(trace)):
                if i > 0:
                    from_node = self._get_or_create_id(
                        self.select_node_info(trace, i - 1))
                else:
                    from_node = 'start'
                to_node = self._get_or_create_id(
                    self.select_node_info(trace, i))
                self._add_node(from_node)
                self._add_node(to_node)
                self._add_edge(from_node, to_node,
                               self.create_edge_label(self.select_edge_info(trace[i])))

        # Set the final trace and add any missing nodes/edges
        self.final_trace = ['start']
        for i in range(len(info.current_trace)):
            if i > 0:
                from_node = self._get_or_create_id(
                    self.select_node_info(info.current_trace, i - 1))
            else:
                from_node = 'start'
            to_node = self._get_or_create_id(
                self.select_node_info(info.current_trace, i))
            self.final_trace.append(to_node)
            self._add_node(from_node)
            self._add_node(to_node)
            self._add_edge(from_node, to_node,
                           self.create_edge_label(self.select_edge_info(info.current_trace[i])))

    def get_final_trace(self) -> list[str]:
        """
        Get the final trace as ordered node ids.
        Edges are subsequent entries in the list.
        """
        return self.final_trace

    def _get_or_create_id(self, info: NodeInfo) -> str:
        """
        Get the ID for a state that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            if self.ids[i] == info:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = info
        return new_id

    def _add_node(self, node: str):
        """
        Add node if it doesn't already exist.
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(
                node, label=self.create_node_label(self.ids[node]))

    def _add_edge(self, from_node: str, to_node: str, label: str):
        """
        Add edge if it doesn't already exist.
        If edge exists, update the label information
        """
        if (from_node, to_node) in self.networkx.edges:
            if label == '':
                return
            old_label = nx.get_edge_attributes(self.networkx, 'label')[
                (from_node, to_node)]
            if label in old_label.split('\n'):
                return
            new_label = old_label + '\n' + label
            attr = {(from_node, to_node): {'label': new_label}}
            nx.set_edge_attributes(self.networkx, attr)
        else:
            self.networkx.add_edge(
                from_node, to_node, label=label)

    @staticmethod
    @abstractmethod
    def select_node_info(pair: list[tuple[ScenarioInfo, StateInfo]], index: int) -> NodeInfo:
        """
        Select the info to use to compare nodes and generate their labels for a specific graph type.
        """
        pass

    @staticmethod
    @abstractmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> EdgeInfo:
        """
        Select the info to use to generate the label for each edge for a specific graph type.
        """
        pass

    @staticmethod
    @abstractmethod
    def create_node_label(info: NodeInfo) -> str:
        """
        Create the label for a node given its chosen information.
        """
        pass

    @staticmethod
    @abstractmethod
    def create_edge_label(info: EdgeInfo) -> str:
        """
        Create the label for an edge given its chosen information.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_legend_info_final_trace_node() -> str:
        """
        Get the information to include in the legend for nodes that appear in the final trace.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_legend_info_other_node() -> str:
        """
        Get the information to include in the legend for nodes that do not appear in the final trace.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_legend_info_final_trace_edge() -> str:
        """
        Get the information to include in the legend for edges that appear in the final trace.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_legend_info_other_edge() -> str:
        """
        Get the information to include in the legend for edges that do not appear in the final trace.
        """
        pass
