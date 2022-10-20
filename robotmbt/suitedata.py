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

class Suite:
    def __init__(self, name, parent=None):
        self.name = name
        self.filename = ''
        self.parent = parent
        self.suites = []
        self.scenarios = []
        self.setup = None # Can be a single step or None
        self.teardown = None # Can be a single step or None

class Scenario:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.setup = None # Can be a single step or None
        self.teardown = None # Can be a single step or None
        self.steps = []

class Step:
    def __init__(self, name, parent):
        self.keyword = name      # first cell of the Robot line, including step_kw, excluding args
        self.parent = parent     # Parent scenario for easy searching and processing
        self._gherkin_kw = None  # 'given', 'when', 'then' or None for non-bdd keywords
        self.args = ()           # Comes directly from Robot
        self.model_info = dict() # Modelling information is available as a dictionary.
                                 # The standard format is dict(IN=[], OUT=[]) and can
                                 # optionally contain an error field.
                                 # IN and OUT are lists of Python evaluatable expressions.
                                 # The `new vocab` form can be used to create new domain objects.
                                 # The `vocab.attribute` form can then be used to express relations
                                 # between properties from the domain vocabulaire.
                                 # Custom processors can define their own attributes.

    @property
    def gherkin_kw(self):
        return self._gherkin_kw

    @gherkin_kw.setter
    def gherkin_kw(self, value):
        self._gherkin_kw = value.lower() if value else None

    @property
    def step_kw(self):
        first_word = self.keyword.split()[0]
        return first_word if first_word.lower() in ['given','when','then','and','but'] else None

    @property
    def bare_kw(self):
        """The keyword without its Gherkin keyword. I.e., as it is known in Robot framework."""
        return self.keyword.replace(self.step_kw, '', 1).strip() if self.step_kw else self.keyword
