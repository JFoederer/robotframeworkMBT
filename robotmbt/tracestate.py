# -*- coding: utf-8 -*-

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

from robotmbt.modelspace import ModelSpace
from robotmbt.suitedata import Scenario


class TraceSnapShot:
    def __init__(self, id: str, inserted_scenario: Scenario, model_state: ModelSpace,
                 remainder: Scenario | None = None, drought: int = 0):
        self.id: str = id
        self.scenario: Scenario = inserted_scenario
        self.remainder: Scenario | None = remainder
        self._model: ModelSpace = model_state.copy()
        self.coverage_drought: int = drought

    @property
    def model(self):
        return self._model.copy()


class TraceState:
    def __init__(self, scenario_indexes: list[int]):
        self.c_pool: dict[int, int] = {index: 0 for index in scenario_indexes}
        if len(self.c_pool) != len(scenario_indexes):
            raise ValueError("Scenarios must be uniquely identifiable")
        self._tried: list[list[int]] = [[]]  # Keeps track of the scenarios already tried at each step in the trace
        self._snapshots: list[TraceSnapShot] = []  # Keeps details for elements in trace
        self._open_refinements: list[int] = []

    @property
    def model(self) -> ModelSpace | None:
        """returns the model as it is at the end of the current trace"""
        return self._snapshots[-1].model if self._snapshots else None

    @property
    def tried(self) -> tuple[int, ...]:
        """returns the indices that were rejected or previously inserted at the current position"""
        return tuple(self._tried[-1])

    @property
    def coverage_drought(self) -> int:
        """Number of scenarios since last new coverage"""
        return self._snapshots[-1].coverage_drought if self._snapshots else 0

    @property
    def id_trace(self):
        return [snap.id for snap in self._snapshots]

    @property
    def active_refinements(self):
        return self._open_refinements[:]

    def coverage_reached(self):
        return all(self.c_pool.values())

    def get_trace(self) -> list[Scenario]:
        return [snap.scenario for snap in self._snapshots]

    def next_candidate(self, retry: bool = False):
        for i in self.c_pool:
            if i not in self._tried[-1] and not self.is_refinement_active(i) and self.count(i) == 0:
                return i
        if not retry:
            return None
        for i in self.c_pool:
            if i not in self._tried[-1] and not self.is_refinement_active(i):
                return i
        return None

    def count(self, index: int) -> int:
        """
        Count the number of times the index is present in the trace.
        unfinished partial scenarios are excluded.
        """
        return self.c_pool[index]

    def highest_part(self, index: int) -> int:
        """
        Given the current trace and an index, returns the highest part number of an ongoing
        refinement for the related scenario. Returns 0 when there is no refinement active.
        """
        for i in range(1, len(self.id_trace) + 1):
            if self.id_trace[-i] == f'{index}':
                return 0
            if self.id_trace[-i].startswith(f'{index}.'):
                return int(self.id_trace[-i].split('.')[1])
        return 0

    def is_refinement_active(self, index: int | None = None) -> bool:
        """
        When called with an index, returns True if that scenario is currently being refined
        When index is ommitted, return True if any refinement is active
        """
        if index is None:
            return self._open_refinements != []
        else:
            return self.highest_part(index) != 0

    def get_remainder(self, index: int) -> Scenario | None:
        """
        When pushing a partial scenario, the remainder can be passed along for safe keeping.
        This method retrieves the remainder for the last part that was pushed.
        """
        last_part = self.highest_part(index)
        index = -self.id_trace[::-1].index(f'{index}.{last_part}') - 1
        return self._snapshots[index].remainder

    def reject_scenario(self, i_scenario: int):
        """Trying a scenario excludes it from further cadidacy on this level"""
        self._tried[-1].append(i_scenario)

    def confirm_full_scenario(self, index: int, scenario: Scenario, model: ModelSpace):
        c_drought = 0 if self.c_pool[index] == 0 else self.coverage_drought + 1
        self.c_pool[index] += 1
        if self.is_refinement_active(index):
            id = f"{index}.0"
            self._open_refinements.pop()
        else:
            id = str(index)
            self._tried[-1].append(index)
            self._tried.append([])
        self._snapshots.append(TraceSnapShot(id, scenario, model, drought=c_drought))

    def push_partial_scenario(self, index: int, scenario: Scenario, model: ModelSpace, remainder=None):
        if self.is_refinement_active(index):
            id = f"{index}.{self.highest_part(index) + 1}"
        else:
            id = f"{index}.1"
            self._tried[-1].append(index)
            self._open_refinements.append(index)
        self._tried.append([])
        self._snapshots.append(TraceSnapShot(id, scenario, model, remainder, self.coverage_drought))

    def can_rewind(self) -> bool:
        return len(self._snapshots) > 0

    def rewind(self) -> TraceSnapShot | None:
        id = self._snapshots[-1].id
        index = int(id.split('.')[0])
        self._snapshots.pop()
        if id.endswith('.0'):
            self.c_pool[index] -= 1
            self._open_refinements.append(index)
            while self._snapshots[-1].id != f"{index}.1":
                self.rewind()
            return self.rewind()

        self._tried.pop()
        if '.' not in id:
            self.c_pool[index] -= 1
        if id.endswith('.1'):
            self._open_refinements.pop()
        return self._snapshots[-1] if self._snapshots else None

    def __iter__(self):
        return iter(self._snapshots)

    def __getitem__(self, key):
        return self._snapshots[key]

    def __len__(self):
        return len(self._snapshots)
