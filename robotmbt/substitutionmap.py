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


class SubstitutionMap:
    """
    A substitution map takes a set of example values that each have a set of
    options from which to pick their concrete values. To narrow down the amount
    of options, multiple calls to substitute() can be made with additional
    constraints. solve() takes the current set of example values and assigns
    a unique concrete value to each.
    """
    def __init__(self):
        self.substitutions = {} # {example_value:Constraint}
        self.solution = {}      # {example_value:solution_value}

    def __str__(self):
        src = self.solution or self.substitutions
        return ", ".join([f"{k} ⤝ {v}" for k, v in src.items()])

    def copy(self):
        new = SubstitutionMap()
        new.substitutions = {k: v.copy() for k,v in self.substitutions.items()}
        new.solution = self.solution.copy()
        return new

    def substitute(self, example_value, constraint=None):
        self.solution = {}
        if example_value in self.substitutions:
            self.substitutions[example_value].add_constraint(constraint)
        else:
            self.substitutions[example_value] = Constraint(constraint)

    def solve(self):
        self.solution = {}
        solution = dict()
        substitutions = self.copy().substitutions
        for example_value in substitutions:
            solution[example_value] = random.choice(list(substitutions[example_value].optionset))
            for other in [e for e in substitutions if e is not example_value]:
                try:
                    substitutions[other].add_constraint([e for e in substitutions[other] if e != solution[example_value]])
                except ValueError:
                    raise ValueError("No solution found within the set of given constraints")
        self.solution = solution
        return solution


class Constraint:
    def __init__(self, constraint):
        try:
            self.optionset = set(constraint)
        except:
            self.optionset = None
        if not self.optionset or isinstance(constraint, str):
            raise ValueError(f"Invalid option set for initial constraint: {constraint}")

    def __repr__(self):
        return f'Constraint([{", ".join([str(e) for e in self.optionset])}])'

    def __iter__(self):
        return iter(self.optionset)

    def copy(self):
        return Constraint(self.optionset)

    def add_constraint(self, constraint):
        if constraint is None: return
        self.optionset = self.optionset.intersection(constraint)
        if not len(self.optionset):
            raise ValueError('No options left after adding constraint')
