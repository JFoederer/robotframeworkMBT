from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, ScenarioInfo
import networkx as nx


class ScenarioGraph(AbstractGraph):
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

    def __init__(self):
        # We use simplified IDs for nodes, and store the actual scenario info here
        self.ids: dict[str, ScenarioInfo] = {}

        # The networkx graph is a directional graph
        self.networkx = nx.DiGraph()

        # add the start node
        self.networkx.add_node('start', label='start')

        # indicates last scenario of trace
        self.end_node = 'start'

    def update_visualisation(self, info: TraceInfo):
        """
        This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
        """
        for i in range(0, len(info.trace) - 1):
            from_node = self._get_or_create_id(info.trace[i])
            to_node = self._get_or_create_id(info.trace[i + 1])

            self._add_node(from_node)
            self._add_node(to_node)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(
                    from_node, to_node, label='')

    def _get_or_create_id(self, scenario: ScenarioInfo) -> str:
        """
        Get the ID for a scenario that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            # TODO: decide how to deal with repeating scenarios, this merges repeated scenarios into a single scenario
            if self.ids[i].src_id == scenario.src_id and scenario.src_id is not None:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = scenario
        return new_id

    def _add_node(self, node: str):
        """
        Add node if it doesn't already exist.
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=self.ids[node].name)

    def _set_starting_node(self, scenario: ScenarioInfo):
        """
        Update the starting node.
        """
        node = self._get_or_create_id(scenario)
        self._add_node(node)
        self.networkx.add_edge('start', node, label='')

    def _set_ending_node(self, scenario: ScenarioInfo):
        """
        Update the end node.
        """
        self.end_node = self._get_or_create_id(scenario)

    def set_final_trace(self, info: TraceInfo):
        """
        Update the graph with information on the final trace.
        """
        self._set_starting_node(info.trace[0])
        self._set_ending_node(info.trace[-1])

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
