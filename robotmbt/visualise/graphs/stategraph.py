from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, StateInfo
from robotmbt.modelspace import ModelSpace
import networkx as nx


class StateGraph(AbstractGraph):
    """
    The state graph is a more advanced representation of trace exploration, allowing you to see the internal state.
    It represents states as nodes, and scenarios as edges.
    """

    def __init__(self):
        # We use simplified IDs for nodes, and store the actual state info here
        self.ids: dict[str, StateInfo] = {}

        # The networkx graph is a directional graph
        self.networkx = nx.DiGraph()

        # add the start node
        self.networkx.add_node('start', label='start')

        self.prev_state = StateInfo(ModelSpace())
        self.prev_trace_len = 0

    def update_visualisation(self, info: TraceInfo):
        """
        This will add nodes the newly reached state (if we did not roll back), as well as an edge from the previous to
        the current state labeled with the scenario that took it there.
        """
        if len(info.trace) > 0:
            scenario = info.trace[-1]

            from_node = self._get_or_create_id(self.prev_state)
            if len(info.trace) == 1:
                from_node = 'start'
            to_node = self._get_or_create_id(info.state)

            self._add_node(from_node)
            self._add_node(to_node)

            if self.prev_trace_len < len(info.trace):
                if (from_node, to_node) not in self.networkx.edges:
                    self.networkx.add_edge(
                        from_node, to_node, label=scenario.name)

        self.prev_state = info.state
        self.prev_trace_len = len(info.trace)

    def _get_or_create_id(self, state: StateInfo) -> str:
        """
        Get the ID for a state that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            if self.ids[i] == state:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = state
        return new_id

    def _add_node(self, node: str):
        """
        Add node if it doesn't already exist.
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=str(self.ids[node]))

    def set_final_trace(self, info: TraceInfo):
        self._set_ending_node(info.state)

    def _set_ending_node(self, state: StateInfo):
        """
        Update the end node.
        """
        self.end_node = self._get_or_create_id(state)

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
