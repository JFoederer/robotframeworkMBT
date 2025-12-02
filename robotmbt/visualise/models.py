from typing import Any

from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario
from robotmbt.tracestate import TraceState


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

    @classmethod
    def _create_state_with_prop(cls, name: str, attrs: list[tuple[str, Any]]):
        space = ModelSpace()
        prop = ModelSpace()
        for (key, val) in attrs:
            prop.__setattr__(key, val)
        space.props[name] = prop
        return cls(space)

    def __init__(self, state: ModelSpace):
        self.domain = state.ref_id

        # Extract all attributes/properties stored in the model space and store them in the temp dict
        # Similar in workings to ModelSpace's get_status_text
        temp = {}
        for p in state.props:
            temp[p] = {}
            if p == 'scenario':
                temp['scenario'] = dict(state.props['scenario'])
            else:
                for attr in dir(state.props[p]):
                    temp[p][attr] = getattr(state.props[p], attr)

        # Filter empty entries
        self.properties = {}
        for p in temp.keys():
            if len(temp[p]) > 0:
                self.properties[p] = temp[p].copy()

    def __eq__(self, other):
        return self.domain == other.domain and self.properties == other.properties

    def __str__(self):
        res = ""
        for p in self.properties:
            if res != "":
                res += "\n\n"
            res += f"{p}:"
            for k, v in self.properties[p].items():
                res += f"\n\t{k}={v}"
        return res


class TraceInfo:
    """
    This contains all information we need at any given step in trace exploration:
    - trace: the strung together scenarios up until this point
    - state: the model space
    """

    @classmethod
    def from_trace_state(cls, trace: TraceState, state: ModelSpace):
        return cls([ScenarioInfo(t) for t in trace.get_trace()], StateInfo(state))

    def __init__(self, trace: list[ScenarioInfo], state: StateInfo):
        self.trace: list[ScenarioInfo] = trace
        self.state = state

    def __repr__(self) -> str:
        return f"TraceInfo(trace=[{[str(t) for t in self.trace]}], state={self.state})"

    def contains_scenario(self, scen_name: str) -> bool:
        for scenario in self.trace:
            if scenario.name == scen_name:
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
            raise IndexError(
                f"InsertTraceAt received invalid index ({index}) for length of list ({len(self.trace)})")

        self.trace.insert(index, scen_info)
