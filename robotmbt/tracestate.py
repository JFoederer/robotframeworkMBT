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

from .modelspace import ModelSpace

class TraceState:
    def __init__(self, n_scenarios):
        self._c_pool = [False] * n_scenarios # coverage pool: True means scenario is in trace
        self._tried = [[]]   # Keeps track of the scenarios already tried at each step in the trace
        self._trace = []     # Choice trace, when was which scenario inserted (e.g. ['1', '2.1', '3', '2.0'])
        self._snapshots = [] # Keeps details for elements in trace

    @property
    def model(self):
        """returns the model as it is at the end of the current trace"""
        return self._snapshots[-1].model if self._trace else ModelSpace()

    @property
    def tried(self):
        """returns the indices that were rejected or previously inserted at the current position"""
        return tuple(self._tried[-1])

    def coverage_reached(self):
        return all(self._c_pool)

    def get_trace(self):
        return [snap.scenario for snap in self._snapshots]

    def next_candidate(self, retry=False):
        for i in range(len(self._c_pool)):
            if i not in self._tried[-1] and self.count(i) == 0 and not self._is_refinement_active(i):
                return i
        if not retry:
            return None
        for i in range(len(self._c_pool)):
            if i not in self._tried[-1]:
                return i
        return None

    def count(self, index):
        """Count the number of times the index is present in the trace.
        unfinished partial scenarios are excluded."""
        return self._trace.count(str(index)) + self._trace.count(str(f"{index}.0"))

    def highest_part(self, index):
        """Given the current trace and an index, returns the highest part number of an ongoing
        refinement for the related scenario. Returns 0 when there is no refinement active."""
        for i in range(1, len(self._trace)+1):
            if self._trace[-i] == f'{index}':
                return 0
            if self._trace[-i].startswith(f'{index}.'):
                return int(self._trace[-i].split('.')[1])
        return 0

    def _is_refinement_active(self, index):
        return self.highest_part(index) != 0

    def reject_scenario(self, i_scenario):
        """Trying a scenario excludes it from further cadidacy on this level"""
        self._tried[-1].append(i_scenario)

    def confirm_full_scenario(self, index, scenario, model):
        self._c_pool[index] = True
        if self._is_refinement_active(index):
            id = f"{index}.0"
        else:
            id = str(index)
            self._tried[-1].append(index)
            self._tried.append([])
        self._trace.append(id)
        self._snapshots.append(TraceSnapShot(id, scenario, model))

    def push_partial_scenario(self, index, scenario, model):
        if self._is_refinement_active(index):
            id = f"{index}.{self.highest_part(index)+1}"
        else:
            id = f"{index}.1"
            self._tried[-1].append(index)
            self._tried.append([])
        self._trace.append(id)
        self._snapshots.append(TraceSnapShot(id, scenario, model))

    def can_rewind(self):
        return len(self._trace) > 0

    def rewind(self):
        id = self._trace.pop()
        index = int(id.split('.')[0])
        if id.endswith('.0'):
            self._snapshots.pop()
            while self._trace[-1] != f"{index}.1":
                self.rewind()
            return self.rewind()

        self._snapshots.pop()
        if '.' not in id or id.endswith('.1'):
            if self.count(index) == 0:
                self._c_pool[index] = False
            self._tried.pop()
        return self._snapshots[-1] if self._snapshots else None

    def __iter__(self):
        return iter(self._snapshots)

    def __getitem__(self, key):
        return self._snapshots[key]

    def __len__(self):
        return len(self._snapshots)

class TraceSnapShot:
    def __init__(self, id, inserted_scenario, model_state):
        self.id = id
        self.scenario = inserted_scenario
        self.model = model_state.copy()
