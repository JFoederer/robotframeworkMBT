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
            self.name = scenario.name
            self.src_id = scenario.src_id
        else:
            self.name = scenario
            self.src_id = None

    def __str__(self):
        return f"Scen{self.src_id}: {self.name}"


class TraceInfo:
    """
    This contains all information we need at any given step in trace exploration:
    - trace: the strung together scenarios up until this point
    - state: the model space
    """

    def __init__(self, trace: TraceState, state: ModelSpace):
        self.trace = [ScenarioInfo(s) for s in trace.get_trace()]
        # TODO: actually use state
        self.state = state


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

        # List of nodes which positions cannot be changed
        self.fixed = []

        # add the start node
        self.networkx.add_node('start')

    def update_visualisation(self, info: TraceInfo):
        """
        Update the visualisation with new trace information from another exploration step.
        This will add nodes for all new scenarios in the provided trace, as well as edges for all pairs in the provided trace.
        """
        for i in range(0, len(info.trace) - 1):
            from_node = self.__get_or_create_id(info.trace[i])
            to_node = self.__get_or_create_id(info.trace[i + 1])

            if from_node not in self.networkx.nodes:
                self.networkx.add_node(
                    from_node, text=self.ids[from_node].name)
            if to_node not in self.networkx.nodes:
                self.networkx.add_node(to_node, text=self.ids[to_node].name)

            if (from_node, to_node) not in self.networkx.edges:
                self.networkx.add_edge(from_node, to_node)

    def __get_or_create_id(self, scenario: ScenarioInfo) -> str:
        """
        Get the ID for a scenario that has been added before, or create and store a new one.
        """
        for i in self.ids.keys():
            # TODO: decide how to deal with repeating scenarios, this merges repeated scenarios into a single scenario
            if self.ids[i].src_id == scenario.src_id:
                return i

        new_id = f"node{len(self.ids)}"
        self.ids[new_id] = scenario
        return new_id

    def set_starting_node(self, scenario: ScenarioInfo):
        """
        Update the starting node.
        """
        node = self.__get_or_create_id(scenario)
        self.networkx.add_edge('start', node)

    def set_ending_node(self, scenario: ScenarioInfo):
        """
        Update the end node.
        """
        node = self.__get_or_create_id(scenario)
        self.fixed.append(node)

    def calculate_pos(self):
        """
        Calculate the position (x, y) for all nodes in self.networkx
        """
        try:
            self.pos = nx.planar_layout(self.networkx)
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.pos = nx.arf_layout(self.networkx, seed=42)
