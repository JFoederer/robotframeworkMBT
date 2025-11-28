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
        self.final_trace: list[str] = ['start']

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

            if i == 0 and ('start', from_node) not in self.networkx.edges:
                self.networkx.add_edge('start', from_node, label='')

    def set_final_trace(self, info: TraceInfo):
        self.final_trace.extend(map(lambda s: self._get_or_create_id(s), info.trace))

    def get_final_trace(self) -> list[str]:
        return self.final_trace

    def _get_or_create_id(self, scenario: ScenarioInfo) -> str:
        """
        Get the ID for a scenario that has been added before, or create and store a new one.
        """
        if scenario.src_id is not None:
            for i in self.ids.keys():
                # TODO: decide how to deal with repeating scenarios, this merges repeated scenarios into a single scenario
                if self.ids[i].src_id == scenario.src_id:
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

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
