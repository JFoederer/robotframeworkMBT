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

    @not_keyword
    def process_test_suite(self, in_suite, coverage='*'):
        self.out_suite = Suite(in_suite.name)
        self.out_suite.filename = in_suite.filename
        self.out_suite.parent = in_suite.parent
        self.flat_suite = self.flatten(in_suite)
        bup_flat_suite = copy.deepcopy(self.flat_suite)
        model = ModelSpace()
        inner_attempts_left = MAX_ATTEMPTS # Tries to find the next suitable scenario,
                                           # given the already selected scenarios
        outer_attempts_left = MAX_ATTEMPTS # Wipes clean any prior choices and starts
                                           # over from scratch
        while self.flat_suite.scenarios and outer_attempts_left:
            while self.flat_suite.scenarios and inner_attempts_left:
                scenario = random.choice(self.flat_suite.scenarios)
                scenario_placed = self._try_to_fit_in_scenario(scenario, model)
                if not scenario_placed:
                    inner_attempts_left -=1
            if self.flat_suite.scenarios:
                logger.info(f"Attempt did not yield a consistent sequence. Retrying...")
                inner_attempts_left = MAX_ATTEMPTS
                outer_attempts_left -=1
                self.flat_suite = copy.deepcopy(bup_flat_suite)
                self.out_suite.scenarios.clear()
                model = ModelSpace()
        if self.flat_suite.scenarios:
            raise Exception("Unable to compose a consistent suite\n"
                           f"last model state:\n{model.get_status_text() or 'empty'}")
        return self.out_suite

    def _try_to_fit_in_scenario(self, scenario, model, running_steps=[]):
        logger.debug(f"Considering scenario {scenario.name}")
        bup_scenario = copy.deepcopy(scenario)
        self.flat_suite.scenarios.remove(scenario)
        if running_steps:
            # running steps indicate that refinement is going on
            # encapsulate this insert scenario in the higher step's conditions
            refined_step = running_steps.pop()
            scenario.steps[0].model_info['IN'] = refined_step.model_info['IN'] +\
                                                 scenario.steps[0].model_info['IN']
            scenario.steps[-1].model_info['OUT'] += refined_step.model_info['OUT']
            scenario.steps = running_steps + scenario.steps
        if self._scenario_can_execute(scenario, model):
            self._process_scenario(scenario, model)
            logger.info(f"Adding scenario {scenario.name}")
            self.out_suite.scenarios.append(scenario)
            return True
        if self._scenario_needs_refinement(scenario, model):
            if not self.flat_suite.scenarios:
                logger.debug("Refinement needed, but there are no scenarios left")
                self.flat_suite.scenarios.append(bup_scenario)
                return False
            refinement_attempts_left = MAX_ATTEMPTS
            ok_steps = self._pop_steps_upto_refinement_point(scenario, model)
            while refinement_attempts_left:
                sub_scenario = random.choice(self.flat_suite.scenarios)
                inserted = self._try_to_fit_in_scenario(sub_scenario, model, ok_steps)
                if inserted:
                    self.flat_suite.scenarios.append(scenario)
                    return self._try_to_fit_in_scenario(scenario, model)
                refinement_attempts_left -=1

        self.flat_suite.scenarios.append(bup_scenario)
        return False

    @staticmethod
    def _scenario_needs_refinement(scenario, model):
        m = copy.deepcopy(model)
        for step in scenario.steps:
            if 'error' in step.model_info:
                return False
            if step.gherkin_kw in ['given', 'when']:
                for expr in step.model_info['IN']:
                    try:
                        if m.process_expression(expr) is False:
                            return False
                    except Exception as err:
                        return False
            if step.gherkin_kw in ['when', 'then']:
                for expr in step.model_info['OUT']:
                    try:
                        if m.process_expression(expr) is False:
                            logger.debug(f"Scenario {scenario.name} needs refinement")
                            return True
                    except Exception as err:
                        return False
        return False

    @staticmethod
    def _pop_steps_upto_refinement_point(scenario, model):
        m = copy.deepcopy(model)
        popped = []
        while scenario.steps:
            step = scenario.steps[0]
            if step.gherkin_kw in ['given', 'when']:
                for expr in step.model_info['IN']:
                    m.process_expression(expr)
            if step.gherkin_kw in ['when', 'then']:
                for expr in step.model_info['OUT']:
                    if m.process_expression(expr) is False:
                        popped.append(copy.deepcopy(step))
                        step.model_info = dict(IN=[], OUT=[])
                        return popped
            popped.append(scenario.steps.pop(0))
        assert False, "pop_steps_upto_refinement_point() called on non-refineable scenario"

    @staticmethod
    def _process_scenario(scenario, model):
        for step in scenario.steps:
            for expr in SuiteProcessors._relevant_expressions(step):
                if expr.lower() != 'none':
                    logger.debug(f"processing {expr}")
                model.process_expression(expr)

    @staticmethod
    def _scenario_can_execute(scenario, model):
        m = copy.deepcopy(model)
        for step in scenario.steps:
            if 'error' in step.model_info:
                logger.debug(f"Error in scenario {scenario.name} at step {step.keyword}: {step.model_info['error']}")
                return False
            for expr in SuiteProcessors._relevant_expressions(step):
                try:
                    if m.process_expression(expr) is False:
                        logger.debug(f"Scenario {scenario.name} failed at step {step.keyword}: {expr} is False")
                        return False
                except Exception as err:
                    logger.debug(f"Error in scenario {scenario.name} at step {step.keyword}: [{expr}] {err}")
                    return False
        return True

    @staticmethod
    def _relevant_expressions(step):
        expressions = []
        if step.gherkin_kw in ['given', 'when']:
            expressions += step.model_info['IN']
        if step.gherkin_kw in ['when', 'then']:
            expressions += step.model_info['OUT']
        return expressions
