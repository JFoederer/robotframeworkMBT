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

import copy

from .modelspace import ModelSpace

class TraceState:
    def __init__(self, n_scenarios):
        self._c_pool = [False] * n_scenarios # coverage pool: True means scenario is in trace
        self._tried = [[]]  # Keeps track of the scenarios tried at each step in the trace
        self._trace = []    # choice trace, when was which scenario inserted
        self._d_trace = []  # Detailed traced, including partial scenarios due to refinement
        self._tracedict = dict() # Keeps details for elements in d_trace

    @property
    def model(self):
        """returns the model as it is at the end of the current trace"""
        return self._tracedict[self._d_trace[-1]].model if self._d_trace else ModelSpace()

    def coverage_reached(self):
        return all(self._c_pool)

    def get_trace(self):
        return [self._tracedict[t].scenario for t in self._d_trace]

    def next_candidate(self):
        for i in range(len(self._c_pool)):
            if i not in self._trace and i not in self._tried[-1]:
                return i
        return None

    def reject_scenario(self, i_scenario):
        """Trying a scenario excludes it from further cadidacy on this level"""
        self._tried[-1].append(i_scenario)

    def confirm_full_scenario(self, index, scenario, model):
        self._c_pool[index] = True
        self._tried[-1].append(index)
        self._tried.append([])
        self._trace.append(index)
        self._d_trace.append(index)
        self._tracedict[index] = TraceSnapShot(scenario, model)

    def can_rewind(self):
        return len(self._d_trace)

    def rewind(self):
        ditch = self._trace.pop()
        self._c_pool[ditch] = False
        self._tried.pop()
        return self._tracedict.pop(self._d_trace.pop())


class TraceSnapShot:
    def __init__(self, inserted_scenario, model_state):
        self.scenario = inserted_scenario
        self.model = model_state.copy()
        self.remainder = None
