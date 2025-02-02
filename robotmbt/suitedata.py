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
from robot.libraries.BuiltIn import BuiltIn

from .steparguments import StepArgument, StepArguments

class Suite:
    def __init__(self, name, parent=None):
        self.name = name
        self.filename = ''
        self.parent = parent
        self.suites = []
        self.scenarios = []
        self.setup = None # Can be a single step or None
        self.teardown = None # Can be a single step or None

    @property
    def longname(self):
        return f"{self.parent.longname}.{self.name}" if self.parent else self.name

    def has_error(self):
        return (  (self.setup.has_error() if self.setup else False)
               or any([s.has_error() for s in self.suites])
               or any([s.has_error() for s in self.scenarios])
               or (self.teardown.has_error() if self.teardown else False))

    def steps_with_errors(self):
        return ( ([self.setup] if self.setup and self.setup.has_error() else [])
               + [e for s in map(Suite.steps_with_errors, self.suites) for e in s]
               + [e for s in map(Scenario.steps_with_errors, self.scenarios) for e in s]
               + ([self.teardown] if self.teardown and self.teardown.has_error() else []))

class Scenario:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent # Parent scenario for easy searching, processing and referencing
                             # after steps and scenarios have been potentially moved around
        self.setup = None    # Can be a single step or None
        self.teardown = None # Can be a single step or None
        self.steps = []

    @property
    def longname(self):
        return f"{self.parent.longname}.{self.name}" if self.parent else self.name

    def has_error(self):
        return ((self.setup.has_error() if self.setup else False)
               or any([s.has_error() for s in self.steps])
               or (self.teardown.has_error() if self.teardown else False))

    def steps_with_errors(self):
        return ( ([self.setup] if self.setup and self.setup.has_error() else [])
               +  [s for s in self.steps if s.has_error()]
               +  ([self.teardown] if self.teardown and self.teardown.has_error() else []))

    def copy(self):
        duplicate = copy.copy(self)
        duplicate.steps = self.steps[:]
        return duplicate

    def split_at_step(self, stepindex):
        """Returns 2 partial scenarios.

        With stepindex 0 the first part has no steps and all steps are in the last part. With
        stepindex 1 the first step is in the first part, the other in the last part, and so on.
        """
        assert stepindex <= len(self.steps), "Split index out of range. Not enough steps in scenario."
        front = Scenario(self.name, self.parent)
        front.setup = self.setup
        front.steps = self.steps[:stepindex]
        back = Scenario(self.name, self.parent)
        back.steps = self.steps[stepindex:]
        back.teardown = self.teardown
        return front, back

class Step:
    def __init__(self, steptext, *args, parent, prev_gherkin_kw=None):
        self.org_step = steptext  # first cell of the Robot line, including step_kw, excluding args
        self.parent = parent      # Parent scenario for easy searching and processing
        self.args = args          # positional and named arguments taken directly from Robot
        self.gherkin_kw = self.step_kw if str(self.step_kw).lower() in ['given', 'when', 'then', 'none'] else prev_gherkin_kw
                                  # 'given', 'when', 'then' or None for non-bdd keywords
        self.signature = None     # Robot keyword with its embedded arguments in ${...} notation
        self.emb_args = StepArguments() # embedded arguments list of StepArgument objects
        self.model_info = dict()  # Modelling information is available as a dictionary.
                                  # The standard format is dict(IN=[], OUT=[]) and can
                                  # optionally contain an error field.
                                  # IN and OUT are lists of Python evaluatable expressions.
                                  # The `new vocab` form can be used to create new domain objects.
                                  # The `vocab.attribute` form can then be used to express relations
                                  # between properties from the domain vocabulaire.
                                  # Custom processors can define their own attributes.
        self.__extract_data_from_robot()

    def __str__(self):
        return f"Step: {self.keyword}"

    def __repr__(self):
        return str(self) + f" with model info: {self.model_info}"

    def has_error(self):
        return 'error' in self.model_info

    def get_error(self):
        return self.model_info.get('error')

    @property
    def keyword(self):
        if not self.signature:
            return self.org_step
        s = f"{self.step_kw} {self.signature}" if self.step_kw else self.signature
        return self.emb_args.fill_in_args(s)

    @property
    def gherkin_kw(self):
        return self._gherkin_kw

    @gherkin_kw.setter
    def gherkin_kw(self, value):
        self._gherkin_kw = value.lower() if value else None

    @property
    def step_kw(self):
        first_word = self.org_step.split()[0]
        return first_word if first_word.lower() in ['given','when','then','and','but'] else None

    @property
    def kw_wo_gherkin(self):
        """The keyword without its Gherkin keyword. I.e., as it is known in Robot framework."""
        return self.keyword.replace(self.step_kw, '', 1).strip() if self.step_kw else self.keyword

    def __extract_data_from_robot(self):
        try:
            runner = BuiltIn()._namespace.get_runner(self.org_step)
            kw = runner.keyword
            if kw.error:
                raise ValueError(kw.error)
            if kw.embedded:
                self.emb_args = StepArguments([StepArgument(*match) for match in
                                 zip(kw.embedded.args, kw.embedded.match(self.kw_wo_gherkin).groups())])
            self.signature = kw.name
            self.model_info = self.__parse_model_info(kw._doc)
        except Exception as ex:
            self.model_info['error']=str(ex)

    def __parse_model_info(self, docu):
        model_info = dict()
        mi_index = docu.find("*model info*")
        if mi_index == -1:
            return model_info
        lines = docu[mi_index:].split('\n')
        lines = [line.strip() for line in lines][1:]
        if "" in lines:
            lines = lines[:lines.index("")]
        format_msg = "*model info* expected format: :<attr>: <expr>|<expr>"
        while lines:
            line = lines.pop(0)
            if not line.startswith(":"):
                raise ValueError(format_msg)
            elms = line.split(":", 2)
            if len(elms) != 3:
                raise ValueError(format_msg)
            key = elms[1].strip()
            expressions = [e.strip() for e in elms[-1].split("|") if e]
            while lines and not lines[0].startswith(":"):
                expressions.extend([e.strip() for e in lines.pop(0).split("|") if e])
            model_info[key] = expressions
        if not model_info:
            raise ValueError("When present, *model info* cannot be empty")
        return model_info
