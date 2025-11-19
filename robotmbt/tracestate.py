# -*- coding: utf-8 -*-
from robotmbt.suitedata import Scenario


# BSD 3-Clause License
#
# Copyright (c) 2022, J. Foederer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

class TraceSnapShot:
    def __init__(self, id: str, inserted_scenario: str | Scenario, model_state: dict[str, int], drought: int = 0):
        self.id: str = id
        self.scenario: str | Scenario = inserted_scenario
        self.model: dict[str, int] = model_state.copy()
        self.coverage_drought: int = drought


class TraceState:
    def __init__(self, n_scenarios: int):
        # coverage pool: True means scenario is in trace
        self._c_pool: list[bool] = [False] * n_scenarios

        # Keeps track of the scenarios already tried at each step in the trace
        self._tried: list[list[int]] = [[]]

        # Choice trace, when was which scenario inserted (e.g. ['1', '2.1', '3', '2.0'])
        self._trace: list[str] = []

        # Keeps details for elements in trace
        self._snapshots: list[TraceSnapShot] = []
        self._open_refinements: list[int] = []

    @property
    def model(self) -> dict[str, int] | None:
        """returns the model as it is at the end of the current trace"""
        return self._snapshots[-1].model if self._trace else None

    @property
    def tried(self) -> tuple[int]:
        """returns the indices that were rejected or previously inserted at the current position"""
        return tuple(self._tried[-1])

    def coverage_reached(self) -> bool:
        return all(self._c_pool)

    @property
    def coverage_drought(self) -> int:
        """Number of scenarios since last new coverage"""
        return self._snapshots[-1].coverage_drought if self._snapshots else 0

    def get_trace(self) -> list[str | Scenario]:
        return [snap.scenario for snap in self._snapshots]

    def next_candidate(self, retry: bool = False) -> int | None:
        for i in range(len(self._c_pool)):
            if i not in self._tried[-1] and not self._is_refinement_active(i) and self.count(i) == 0:
                return i

        if not retry:
            return None

        for i in range(len(self._c_pool)):
            if i not in self._tried[-1] and not self._is_refinement_active(i):
                return i

        return None

    def count(self, index: int) -> int:
        """Count the number of times the index is present in the trace.
        unfinished partial scenarios are excluded."""
        return self._trace.count(str(index)) + self._trace.count(str(f"{index}.0"))

    def highest_part(self, index: int) -> int:
        """Given the current trace and an index, returns the highest part number of an ongoing
        refinement for the related scenario. Returns 0 when there is no refinement active."""
        for i in range(1, len(self._trace) + 1):
            if self._trace[-i] == f'{index}':
                return 0

            if self._trace[-i].startswith(f'{index}.'):
                return int(self._trace[-i].split('.')[1])

        return 0

    def _is_refinement_active(self, index: int) -> bool:
        return self.highest_part(index) != 0

    def find_scenarios_with_active_refinement(self) -> list[str | Scenario]:
        scenarios = []
        for i in self._open_refinements:
            index = -self._trace[::-1].index(f'{i}.1') - 1
            scenarios.append(self._snapshots[index].scenario)

        return scenarios

    def reject_scenario(self, i_scenario: int):
        """Trying a scenario excludes it from further cadidacy on this level"""
        self._tried[-1].append(i_scenario)

    def confirm_full_scenario(self, index: int, scenario: str, model: dict[str, int]):
        if not self._c_pool[index]:
            self._c_pool[index] = True
            c_drought = 0
        else:
            c_drought = self.coverage_drought + 1

        if self._is_refinement_active(index):
            id = f"{index}.0"
            self._open_refinements.pop()
        else:
            id = str(index)
            self._tried[-1].append(index)
            self._tried.append([])

        self._trace.append(id)
        self._snapshots.append(TraceSnapShot(id, scenario, model, c_drought))

    def push_partial_scenario(self, index: int, scenario: str, model: dict[str, int]):
        if self._is_refinement_active(index):
            id = f"{index}.{self.highest_part(index) + 1}"

        else:
            id = f"{index}.1"
            self._tried[-1].append(index)
            self._tried.append([])
            self._open_refinements.append(index)
        self._trace.append(id)
        self._snapshots.append(TraceSnapShot(
            id, scenario, model, self.coverage_drought))

    def can_rewind(self) -> bool:
        return len(self._trace) > 0

    def rewind(self) -> TraceSnapShot | None:
        id = self._trace.pop()
        index = int(id.split('.')[0])
        if id.endswith('.0'):
            self._snapshots.pop()
            self._open_refinements.append(index)
            while self._trace[-1] != f"{index}.1":
                self.rewind()
            return self.rewind()

        self._snapshots.pop()
        if '.' not in id or id.endswith('.1'):
            if self.count(index) == 0:
                self._c_pool[index] = False
            self._tried.pop()

            if id.endswith('.1'):
                self._open_refinements.pop()

        return self._snapshots[-1] if self._snapshots else None

    def __iter__(self):
        return iter(self._snapshots)

    def __getitem__(self, key):
        return self._snapshots[key]

    def __len__(self):
        return len(self._snapshots)
