from abc import ABC, abstractmethod
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
        return f"Scenario {self.src_id}: {self.name}"


class StateInfo:
    """
    This contains all information we need from states, abstracting away from the actual ModelSpace class:
    - domain
    - properties
    """

    def __init__(self, state: ModelSpace):
        self.domain = state.ref_id
        self.properties = {}
        for p in state.props:
            self.properties[p] = {}
            if p == 'scenario':
                self.properties['scenario'] = dict(state.props['scenario'])
            else:
                for attr in dir(state.props[p]):
                    self.properties[p][attr] = getattr(state.props[p], attr)

    def __eq__(self, other):
        return self.domain == other.domain and self.properties == other.properties

    def __str__(self):
        res = ""
        for p in self.properties:
            res += f"{p}:\n"
            for k, v in self.properties[p].items():
                res += f"\t{k}={v}\n"
        return res


class TraceInfo:
    """
    This contains all information we need at any given step in trace exploration:
    - trace: the strung together scenarios up until this point
    - state: the model space
    """

    @classmethod
    def from_trace_state(cls, trace: TraceState, state: ModelSpace):
        return cls([ScenarioInfo(t) for t in trace.get_trace()], state)

    def __init__(self, trace: list[ScenarioInfo], state: ModelSpace):
        self.trace: list[ScenarioInfo] = trace
        self.state = StateInfo(state)

    def __repr__(self) -> str:
        return f"TraceInfo(trace=[{[str(t) for t in self.trace]}], state={self.state})"

    def contains_scenario(self, scen_name: str) -> bool:
        for scen in self.trace:
            if scen.name == scen_name:
                return True
        return False

    def add_scenario(self, scen: ScenarioInfo):
        """
        Used in acceptance testing
        """
        self.trace.append(scen)

    def get_scenario(self, scen_name: str) -> ScenarioInfo | None:
        for scenario in self.trace:
            if scenario.name == scen_name:
                return scenario
        return None

    def insert_trace_at(self, index: int, scen_info: ScenarioInfo):
        if index < 0 or index >= len(self.trace):
            raise IndexError(f"InsertTraceAt received invalid index ({index}) for length of list ({len(self.trace)})")

        self.trace.insert(index, scen_info)


class AbstractGraph(ABC):
    @abstractmethod
    def update_visualisation(self, info: TraceInfo):
        """
        Update the visualisation with new trace information from another exploration step.
        """
        pass

    @abstractmethod
    def set_final_trace(self, info: TraceInfo):
        """
        Update the graph with information on the final trace.
        """
        pass

    @abstractmethod
    def calculate_pos(self):
        """
        Calculate the position (x, y) for all nodes in self.networkx
        """
        pass

    @property
    @abstractmethod
    def networkx(self) -> nx.DiGraph:
        """
        We use networkx to store nodes and edges.
        """
        pass

    @networkx.setter
    @abstractmethod
    def networkx(self, value: nx.DiGraph):
        pass

    @property
    @abstractmethod
    def pos(self) -> dict:
        """
        A dictionary with the positions of nodes.
        """
        pass

    @pos.setter
    @abstractmethod
    def pos(self, value: dict):
        pass


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

        # Stores the position (x, y) of the nodes
        self.pos = {}

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

    def calculate_pos(self):
        try:
            self.pos = nx.planar_layout(self.networkx)
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.pos = nx.arf_layout(self.networkx, seed=42)

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value

    @property
    def pos(self) -> dict:
        return self._pos

    @pos.setter
    def pos(self, value: dict):
        self._pos = value


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

        # Stores the position (x, y) of the nodes
        self.pos = {}

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
                    self.networkx.add_edge(from_node, to_node, label=scenario.name)

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

    def calculate_pos(self):
        try:
            self.pos = nx.planar_layout(self.networkx)
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.pos = nx.arf_layout(self.networkx, seed=42)

    @property
    def networkx(self) -> nx.DiGraph:
        return self._networkx

    @networkx.setter
    def networkx(self, value: nx.DiGraph):
        self._networkx = value

    @property
    def pos(self) -> dict:
        return self._pos

    @pos.setter
    def pos(self, value: dict):
        self._pos = value
