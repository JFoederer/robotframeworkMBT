# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2024, J. Foederer
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

import random

class EquivalenceClass:
    def __init__(self):
        self.substitutions = {} # {example_value:Constraint}
        self.solution = None

    def __repr__(self):
        if self.solution:
            return "EquivalenceClass(%s)" % ", ".join([f"{k} ⤝ {v}" for k, v in self.solution.items()])
        else:
            return f"EquivalenceClass({', '.join(self.substitutions)})"

    def __iter__(self):
        return iter(self.substitutions)

    def copy(self):
        new = EquivalenceClass()
        new.substitutions = {k: v.copy() for k,v in self.substitutions.items()}
        new.solution = self.solution
        return new

    def substitute(self, example_value, constraint=None) -> None:
        self.solution = None
        if example_value in self.substitutions:
            self.substitutions[example_value].add_constraint(constraint)
        else:
            self.substitutions[example_value] = Constraint(constraint)

    def solve(self):
        solution = dict()
        for example_value in self.substitutions:
            solution[example_value] = random.choice(list(self.substitutions[example_value].optionset))
            for other in [e for e in self.substitutions if e is not example_value]:
                self.substitutions[other].add_constraint([e for e in self.substitutions[other] if e != solution[example_value]])
        self.solution = solution
        return solution

class Constraint:
    def __init__(self, constraint):
        try:
            self.optionset = set(constraint)
        except:
            raise ValueError(f"Invalid option set for initial constraint: {constraint}")

    def __repr__(self):
        return f'Constraint([{", ".join([str(e) for e in self.optionset])}])'

    def __iter__(self):
        return iter(self.optionset)

    def copy(self):
        return Constraint(self.optionset)

    def add_constraint(self, constraint):
        if not constraint: return
        self.optionset = self.optionset.intersection(constraint)
        if not len(self.optionset):
            raise ValueError('No options left after adding constraint')
