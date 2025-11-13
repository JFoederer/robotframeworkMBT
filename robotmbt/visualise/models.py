from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState
import networkx as nx


class ScenarioInfo:
    """
    This contains all information we need from scenarios, abstracting away from the actual Scenario class:
    - name
    - src_id
    """

    def __init__(self, scenario: Scenario | str):
        if isinstance(scenario, Scenario):
            # default case
            self.name = scenario.name
            self.src_id = scenario.src_id
        else:
            # unit tests
            self.name = scenario
            self.src_id = scenario

    def __str__(self):
        return f"Scen{self.src_id}: {self.name}"


class TraceInfo:
    """
    This contains all information we need at any given step in trace exploration:
    - trace: the strung together scenarios up until this point
    - state: the model space
    """
    @classmethod
    def from_trace_state(cls, trace: TraceState, state: ModelSpace):
        return cls([ScenarioInfo(t) for t in trace.get_trace()], state)

    def __init__(self, trace :list[ScenarioInfo], state :ModelSpace):
        self.trace :list[ScenarioInfo] = trace
        # TODO: actually use state
        self.state :ModelSpace = state
    
    def __repr__(self) -> str:
        return f"TraceInfo(trace=[{[str(t) for t in self.trace]}], state={self.state})"


class ScenarioGraph:
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

    def __init__(self):
        # We use simplified IDs for nodes, and store the actual scenario info here
        self.ids: dict[str, ScenarioInfo] = {}

        # The networkx graph is a directional graph
        self.networkx = nx.DiGraph()

        # Stores the position (x, y) of the nodes
        self.pos = {}

        # add the start node
        self.networkx.add_node('start', label='start')

        # indicates last scenario of trace
        self.end_node = 'start'

    def update_visualisation(self, info: TraceInfo):
        """
        Update the visualisation with new trace information from another exploration step.
        This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
        """
        for i in range(0, len(info.trace) - 1):
            from_node = self._get_or_create_id(info.trace[i])
            to_node = self._get_or_create_id(info.trace[i + 1])

            self.add_node(from_node)
            self.add_node(to_node)

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

    def add_node(self, node: str):
        """
        Add node if it doesn't already exist
        """
        if node not in self.networkx.nodes:
            self.networkx.add_node(node, label=self.ids[node].name)

    def set_starting_node(self, scenario: ScenarioInfo):
        """
        Update the starting node.
        """
        node = self._get_or_create_id(scenario)
        self.add_node(node)
        self.networkx.add_edge('start', node, label='')

    def set_ending_node(self, scenario: ScenarioInfo):
        """
        Update the end node.
        """
        self.end_node = self._get_or_create_id(scenario)

    def calculate_pos(self):
        """
        Calculate the position (x, y) for all nodes in self.networkx
        """
        try:
            self.pos = nx.planar_layout(self.networkx)
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.pos = nx.arf_layout(self.networkx, seed=42)
