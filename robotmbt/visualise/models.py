import logging
from typing import Any

from robot.api import logger

from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario

import jsonpickle
import tempfile
import os


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

    def __eq__(self, other):
        return self.src_id == other.src_id


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

    def difference(self, new_state) -> set[tuple[str, str]]:
        old: dict[str, dict | str] = self.properties.copy()
        new: dict[str, dict | str] = new_state.properties.copy()
        temp = StateInfo._dict_deep_diff(old, new)
        for key in temp.keys():
            res = ""
            for k, v in sorted(temp[key].items()):
                res += f"\n\t{k}={v}"
            temp[key] = res
        return set(temp.items())  # type inference goes wacky here

    @staticmethod
    def _dict_deep_diff(old_state: dict[str, any], new_state: dict[str, any]) -> dict[str, any]:
        res = {}
        for key in new_state.keys():
            if key not in old_state:
                res[key] = new_state[key]
            elif isinstance(old_state[key], dict):
                diff = StateInfo._dict_deep_diff(old_state[key], new_state[key])
                if len(diff) != 0:
                    res[key] = diff
            elif old_state[key] != new_state[key]:
                res[key] = new_state[key]
        return res


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
    This keeps track of all information we need from all steps in trace exploration:
    - current_trace: the trace currently being built up, a list of scenario/state pairs in order of execution
    - all_traces: all valid traces encountered in trace exploration, up until the point they could not go any further
    - previous_length: used to identify backtracking
    """

    def __init__(self):
        self.current_trace: list[tuple[ScenarioInfo, StateInfo]] = []
        self.all_traces: list[list[tuple[ScenarioInfo, StateInfo]]] = []
        self.previous_length: int = 0
        self.pushed: bool = False
        self.path = "json/"

    def update_trace(self, scenario: ScenarioInfo | None, state: StateInfo, length: int):
        if length > self.previous_length:
            # New state - push
            self._push(scenario, state, length - self.previous_length)
            self.previous_length = length
        elif length < self.previous_length:
            # Backtrack - pop
            self._pop(self.previous_length - length)
            self.previous_length = length

            # Sanity check
            if len(self.current_trace) > 0:
                self._sanity_check(scenario, state, 'popping')
        else:
            # No change - sanity check
            if len(self.current_trace) > 0:
                self._sanity_check(scenario, state, 'nothing')

    def _push(self, scenario: ScenarioInfo, state: StateInfo, n: int):
        if n > 1:
            logger.warn(
                f"Pushing multiple scenario/state pairs at once to trace info ({n})! Some info might be lost!")
        for _ in range(n):
            self.current_trace.append((scenario, state))
        self.pushed = True

    def _pop(self, n: int):
        if self.pushed:
            self.all_traces.append(self.current_trace.copy())
        for _ in range(n):
            self.current_trace.pop()
        self.pushed = False

    def encountered_scenarios(self) -> set[ScenarioInfo]:
        res = set()

        for trace in self.all_traces:
            for (scenario, state) in trace:
                res.add(scenario)

        return res

    def encountered_states(self) -> set[StateInfo]:
        res = set()

        for trace in self.all_traces:
            for (scenario, state) in trace:
                res.add(state)

        return res

    def encountered_scenario_state_pairs(self) -> set[tuple[ScenarioInfo, StateInfo]]:
        res = set()

        for trace in self.all_traces:
            for (scenario, state) in trace:
                res.add((scenario, state))

        return res

    def __repr__(self) -> str:
        return f"TraceInfo(traces=[{[f'[{[self.stringify_pair(pair) for pair in trace]}]' for trace in self.all_traces]}], current=[{[self.stringify_pair(pair) for pair in self.current_trace]}])"

    def _sanity_check(self, scen: ScenarioInfo, state: StateInfo, after: str):
        (prev_scen, prev_state) = self.current_trace[-1]
        if prev_scen != scen:
            logger.warn(
                f'TraceInfo got out of sync after {after}\nExpected scenario: {prev_scen}\nActual scenario: {scen}')
        if prev_state != state:
            logger.warn(
                f'TraceInfo got out of sync after {after}\nExpected state: {prev_state}\nActual state: {state}')

    def export_graph(self, suite_name: str, atest: bool = False) -> str | None:
        encoded_instance = jsonpickle.encode(self)
        name = suite_name.lower().replace(' ', '_')
        if atest:
            '''
            temporary file to not accidentaly overwrite an existing file
            mkstemp() is not ideal but given Python's limitations this is the easiest solution
            as temporary file, a different method, is problamatic on Windows 
            https://stackoverflow.com/a/57015383
            '''
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "w") as f:
                f.write(encoded_instance)
            return path

        with open(f"{self.path}{name}.json", "w") as f:
            f.write(encoded_instance)
        return None

    def import_graph(self, file_name: str):
        with open(f"{self.path}{file_name}.json", "r") as f:
            string = f.read()
            self = jsonpickle.decode(string)


    @staticmethod
    def stringify_pair(pair: tuple[ScenarioInfo, StateInfo]) -> str:
        return f"Scenario={pair[0].name}, State={pair[1]}"
