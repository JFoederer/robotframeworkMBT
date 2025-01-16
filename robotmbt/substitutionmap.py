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

    def substitute(self, example_value, constraint):
        self.solution = {}
        if example_value in self.substitutions:
            self.substitutions[example_value].add_constraint(constraint)
        else:
            self.substitutions[example_value] = Constraint(constraint)

    def solve(self):
        self.solution = {}
        solution = dict()
        substitutions = self.copy().substitutions
        sorted_subs = list(substitutions)
        subs_stack = []
        while sorted_subs:
            sorted_subs.sort(key=lambda i: len(substitutions[i].optionset))
            example_value = sorted_subs[0]
            # make a choice for this example
            solution[example_value] = random.choice(list(substitutions[example_value].optionset))
            subs_stack.append(example_value)
            # exclude the choice from all others
            others_list = []
            for other in [e for e in substitutions if e != example_value]:
                others_list.append(other)
                try:
                    substitutions[other].remove_option(solution[example_value])
                except ValueError:
                    # wrong choice, this depletes the last option for another
                    for corrupted_other in others_list:
                        substitutions[corrupted_other].undo_remove()
                    try:
                        substitutions[example_value].remove_option(solution.pop(example_value))
                        break
                    except ValueError:
                        # roll back last choice
                        done = False
                        while not done:
                            try:
                                while subs_stack[-1] == example_value:
                                    substitutions[example_value].undo_remove()
                                    subs_stack.pop()
                                last_item = subs_stack[-1]
                                sorted_subs.insert(0, last_item)
                            except IndexError:
                                raise ValueError("No solution found within the set of given constraints")
                            for previous_dependency in [e for e in substitutions if e != last_item]:
                                substitutions[previous_dependency].undo_remove()
                            try:
                                substitutions[last_item].remove_option(solution.pop(last_item))
                            except ValueError:
                                # next level must also be rolled back
                                example_value = last_item
                                continue
                            done = True
                        break
            else:
                sorted_subs.pop(0)
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
        self.removed_stack = []

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

    def remove_option(self, option):
        try:
            self.optionset.remove(option)
            self.removed_stack.append(option)
        except KeyError:
            self.removed_stack.append(Placeholder)
        if not len(self.optionset):
            raise ValueError('No options left after adding constraint')

    def undo_remove(self):
        last_item = self.removed_stack.pop()
        if last_item is not Placeholder:
            self.optionset.add(last_item)


class Placeholder:
    """For when None isn't specific enough"""
