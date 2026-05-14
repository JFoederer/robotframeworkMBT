# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2026, J. Foederer
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

import unittest

from robotmbt.modeller import process_scenario

from robotmbt.modelspace import ModelSpace


class TestModeller(unittest.TestCase):
    def test_successful_scenario_evaluation(self):
        scenario = ScenarioStub("my scenario")
        scenario.steps.append(StepStub('initialise x', dict(IN=[], OUT=['new model', 'model.x = 0'])))
        scenario.steps.append(StepStub('x should be 0', dict(IN=['model.x == 0'], OUT=[])))
        part1, part2, fail_info = process_scenario(scenario, ModelSpace())
        self.assertEqual(fail_info, {})
        self.assertEqual(part1.name, "my scenario")
        self.assertIsNone(part2)

    def test_scenario_is_rejected_when_condition_evaluates_to_false(self):
        scenario = ScenarioStub()
        scenario.steps.append(StepStub('initialise x', dict(IN=[], OUT=['new model', 'model.x = 0'])))
        scenario.steps.append(StepStub('x should be 2', dict(IN=['model.x == 2'], OUT=[])))
        part1, part2, fail_info = process_scenario(scenario, ModelSpace())
        self.assertEndsWith(fail_info['fail_msg'], "[model.x == 2] is False")

    def test_duplicate_in_out_condition_does_not_refine(self):
        """
        Covers a prior defect where refinement would be entered unintended when the exact expression text
        from an IN-condition that should fail the step, also appeared as an OUT-condition.
        """
        scenario = ScenarioStub()
        scenario.steps.append(StepStub('initialise x', dict(IN=[], OUT=['new model', 'model.x = 0'])))
        scenario.steps.append(StepStub('x should be 2', dict(IN=['model.x == 2'], OUT=['model.x == 2'])))
        part1, part2, fail_info = process_scenario(scenario, ModelSpace())
        self.assertIsNone(part2)
        self.assertEndsWith(fail_info['fail_msg'], "[model.x == 2] is False")


class ScenarioStub:
    def __init__(self, name: str = 'dummy'):
        self.name = name
        self.src_id = 0
        self.steps = []

    def copy(self):
        return ScenarioStub(self.name)


class StepStub:
    def __init__(self, steptext: str, model_info: dict = {}) -> None:
        self.org_step: str = steptext
        first_word = steptext.split()[0].lower()
        self.gherkin_kw = first_word if first_word in ['given', 'when', 'then'] else None
        self.args = ArgStub()
        self.model_info = model_info

    def __str__(self):
        return self.org_step


class ArgStub(list):
    def fill_in_args(self, text, as_code=True):
        return text
