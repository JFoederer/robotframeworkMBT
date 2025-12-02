from robot.api import logger

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, StateInfo
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

        # To check if we've backtracked
        self.prev_trace_len = 0

        # Stack to track the current execution path
        self.node_stack: list[str] = ['start']

    def update_visualisation(self, info: TraceInfo):
        """
        This will add nodes the newly reached state (if we did not roll back), as well as an edge from the previous to
        the current state labeled with the scenario that took it there.
        """
        node = self._get_or_create_id(info.state)

        if self.prev_trace_len < len(info.trace):
            # New state added - add to stack
            push_count = len(info.trace) - self.prev_trace_len
            for i in range(push_count):
                self.node_stack.append(node)
                self._add_node(self.node_stack[-2])
                self._add_node(self.node_stack[-1])

                if (self.node_stack[-2], self.node_stack[-1]) not in self.networkx.edges:
                    self.networkx.add_edge(
                        self.node_stack[-2], self.node_stack[-1], label=info.trace[-push_count + i].name)

        elif self.prev_trace_len > len(info.trace):
            # States removed - remove from stack
            pop_count = self.prev_trace_len - len(info.trace)
            for _ in range(pop_count):
                if len(self.node_stack) > 1:  # Always keep 'start'
                    self.node_stack.pop()
                else:
                    logger.warn("Tried to rollback more than was previously added to the stack!")

        self.prev_trace_len = len(info.trace)

    def set_final_trace(self, info: TraceInfo):
        # We already have the final trace in state_stack, so we don't need to do anything
        # But do a sanity check
        if self.prev_trace_len != len(info.trace):
            logger.warn("Final trace was of a different length than our stack was based on!")

    def get_final_trace(self) -> list[str]:
        # The final trace is simply the state stack we've been keeping track of
        return self.node_stack

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

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
