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

from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import not_keyword
from robot.api import logger

from .suitedata import Suite, Scenario, Step
from .modelspace import ModelSpace

import copy
import random

MAX_ATTEMPTS = 20

class SuiteProcessors:
    @not_keyword
    def echo(self, in_suite, coverage='*'):
        return in_suite

    @not_keyword
    def process_test_suite(self, in_suite, coverage='*'):
        out_suite = Suite(in_suite.name)
        out_suite.filename = in_suite.filename
        out_suite.parent = in_suite.parent
        flat_suite = self.flatten(in_suite)
        bup_flat_suite = copy.deepcopy(flat_suite)
        model = ModelSpace()
        inner_attempts_left = MAX_ATTEMPTS # Tries to find the next suitable sceanrio,
                                           # given the already selected scenarios
        outer_attempts_left = MAX_ATTEMPTS # Wipes clean any prior choices and starts
                                           # over from scratch
        while flat_suite.scenarios and outer_attempts_left:
            while flat_suite.scenarios and inner_attempts_left:
                scenario = random.choice(flat_suite.scenarios)
                if self._scenario_can_execute(scenario, model):
                    logger.info(f"Adding scenario {scenario.name}")
                    self._process_scenario(scenario, model)
                    out_suite.scenarios.append(scenario)
                    flat_suite.scenarios.remove(scenario)
                else:
                    inner_attempts_left -=1
            if flat_suite.scenarios:
                logger.info(f"Attempt did not yield a consistent sequence. Retrying...")
                inner_attempts_left = MAX_ATTEMPTS
                outer_attempts_left -=1
                flat_suite = copy.deepcopy(bup_flat_suite)
                out_suite.scenarios.clear()
                model = ModelSpace()
        if flat_suite.scenarios:
            raise Exception("Unable to compose a consistent suite\n"
                           f"last model state:\n{model.get_status_text() or 'empty'}")
        return out_suite

    @not_keyword
    def flatten(self, in_suite):
        """
        Takes a Suite as input and returns a Suite as output. The output Suite does not
        have any sub-suites, only scenarios. The scenarios do not have a setup. Any setup
        keywords are inserted at the front of the scenario as regular steps.
        """
        out_suite = copy.deepcopy(in_suite)
        outer_scenarios = out_suite.scenarios
        for scenario in outer_scenarios:
            if scenario.setup:
                scenario.steps.insert(0, scenario.setup)
                scenario.setup = None
            if scenario.teardown:
                scenario.steps.append(scenario.teardown)
                scenario.teardown = None
        out_suite.scenarios = []
        for suite in in_suite.suites:
            subsuite = self.flatten(suite)
            for scenario in subsuite.scenarios:
                if subsuite.setup:
                    scenario.steps.insert(0, subsuite.setup)
                if subsuite.teardown:
                    scenario.steps.append(subsuite.teardown)
            out_suite.scenarios.extend(subsuite.scenarios)
        out_suite.scenarios.extend(outer_scenarios)
        out_suite.suites = []
        return out_suite

    @staticmethod
    def _process_scenario(scenario, model):
        for step in scenario.steps:
            for expr in self.relevant_expressions(step):
                model.process_expression(expr)

    @staticmethod
    def _scenario_can_execute(scenario, model):
        m = copy.deepcopy(model)
        for step in scenario.steps:
            if 'error' in step.model_info:
                logger.debug(f"Error in scenario {scenario.name} at step {step.keyword}: {step.model_info['error']}")
                return False
            for expr in self.relevant_expressions(step):
                try:
                    if m.process_expression(expr) is False:
                        logger.debug(f"Scenario {scenario.name} failed at step {step.keyword}: {expr} is False")
                        return False
                except Exception as err:
                    logger.debug(f"Error in scenario {scenario.name} at step {step.keyword}: [{expr}] {err}")
                    return False
        return True

    def relevant_expressions(self, step):
        expressions = []
        if step.gherkin_kw in ['given', 'when']:
            expressions += step.model_info['IN']
        if step.gherkin_kw in ['when', 'then']:
            expressions += step.model_info['OUT']
        return expressions
