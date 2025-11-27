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

        self.start_scenario: ScenarioInfo | None = None
        self.start_state: StateInfo | None = None

        self.prev_state = StateInfo(ModelSpace())
        self.prev_state_len = 0

    def update_visualisation(self, info: TraceInfo):
        """
        This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
        """
        if len(info.trace) == 1:
            self.start_scenario = info.trace[0]
            self.start_state = info.state

        for i in range(0, len(info.trace) - 1):
            from_node = self._get_or_create_id(info.trace[i], self.prev_state)
            to_node = self._get_or_create_id(info.trace[i + 1], info.state)

            self._add_node(from_node)
            self._add_node(to_node)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(
                    from_node, to_node, label='')

        self.prev_state = info.state
        self.prev_state_len = len(info.trace)

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

    def _set_starting_node(self, scenario: ScenarioInfo, state: StateInfo):
        """
        Update the starting node.
        """
        node = self._get_or_create_id(scenario, state)
        self._add_node(node)
        self.networkx.add_edge('start', node, label='')

    def set_final_trace(self, info: TraceInfo):
        """
        Update the graph with information on the final trace.
        """
        if self.start_scenario is None:
            self.start_scenario = info.trace[0]
            self.start_state = info.state  # fallback if a trace with multiple nodes instantly materializes
        first_node = self.ids[self._get_or_create_id(self.start_scenario, self.start_state)]
        self._set_starting_node(first_node[0], first_node[1])

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value
