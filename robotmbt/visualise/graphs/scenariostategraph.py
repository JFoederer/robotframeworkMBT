import networkx as nx

from robotmbt.modelspace import ModelSpace
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo


class ScenarioStateGraph(AbstractGraph):
    """
    The scenario-State graph keeps track of both the scenarios and states encountered.
    Its nodes are scenarios together with the state after the scenario has run.
    Its edges represent steps in the trace.
    """

    def __init__(self):
        # We use simplified IDs for nodes, and store the actual scenario info here
        self.ids: dict[str, tuple[ScenarioInfo, StateInfo]] = {}

        # The networkx graph is a directional graph
        self.networkx = nx.DiGraph()

        # add the start node
        self.networkx.add_node('start', label='start')

        self.prev_state = StateInfo(ModelSpace())
        self.prev_trace_len = 0

        # Stack to track the current execution path
        self.node_stack: list[str] = ['start']

    def update_visualisation(self, info: TraceInfo):
        """
        This will add nodes the newly reached scenario/state pair, as well as an edge from the previous to
        the current scenario/state pair.
        """
        if len(info.trace) == 0:
            self.prev_trace_len = len(info.trace)
            self.prev_state = info.state
            return

        if len(info.trace) == 1:
            from_node = 'start'
        else:
            from_node = self._get_or_create_id(info.trace[-2], self.prev_state)
        to_node = self._get_or_create_id(info.trace[-1], info.state)

        if self.prev_trace_len < len(info.trace):
            # New state added - add to stack
            self.node_stack.append(to_node)

            self._add_node(from_node)
            self._add_node(to_node)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(from_node, to_node, label='')

        elif self.prev_trace_len > len(info.trace):
            # States removed - remove from stack
            pop_count = self.prev_trace_len - len(info.trace)
            for _ in range(pop_count):
                if len(self.node_stack) > 1:  # Always keep 'start'
                    self.node_stack.pop()

        self.prev_state = info.state
        self.prev_trace_len = len(info.trace)

    def set_final_trace(self, info: TraceInfo):
        # We already have the final trace in state_stack, so we don't need to do anything
        pass

    def get_final_trace(self) -> list[str]:
        # The final trace is simply the state stack we've been keeping track of
        return self.node_stack

    def _get_or_create_id(self, scenario: ScenarioInfo, state: StateInfo) -> str:
        """
        Get the ID for a scenario that has been added before, or create and store a new one.
        """
        if scenario.src_id is not None:
            for i in self.ids.keys():
                if self.ids[i][0].src_id == scenario.src_id and self.ids[i][1] == state:
                    return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = (scenario, state)
        return new_id

    @staticmethod
    def _gen_label(scenario: ScenarioInfo, state: StateInfo) -> str:
        """
        Creates the label for a node in a Scenario-State Graph from the scenario and state associated to it.
        """
        return scenario.name + "\n\r" + str(state)

    def _add_node(self, node: str):
        """
        Add node if it doesn't already exist.
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=self._gen_label(self.ids[node][0], self.ids[node][1]))

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
