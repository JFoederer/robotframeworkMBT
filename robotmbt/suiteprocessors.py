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
        while self.flat_suite.scenarios:
            while self.flat_suite.scenarios and inner_attempts_left:
                selected_scenario = random.choice(self.flat_suite.scenarios)
                self.flat_suite.scenarios.remove(selected_scenario)
                new_model = self._try_to_fit_in_scenario(selected_scenario, model)
                if new_model:
                    model = new_model
                else:
                    inner_attempts_left -=1
                    self.flat_suite.scenarios.append(selected_scenario)
            if self.flat_suite.scenarios:
                outer_attempts_left -=1
                if not outer_attempts_left:
                    break
                logger.debug(f"model state:\n{model.get_status_text()}")
                logger.debug(f"Remaining scenarios: {[s.name for s in self.flat_suite.scenarios]}")
                logger.info(f"Attempt did not yield a consistent sequence. Retrying...")
                inner_attempts_left = MAX_ATTEMPTS
                self.flat_suite = copy.deepcopy(bup_flat_suite)
                self.out_suite.scenarios.clear()
                model = ModelSpace()
        if self.flat_suite.scenarios:
            raise Exception("Unable to compose a consistent suite\n"
                           f"last model state:\n{model.get_status_text() or 'empty'}")
        return self.out_suite

    def _try_to_fit_in_scenario(self, scenario, model):
        logger.debug(f"Considering scenario {scenario.name}")
        bup_model = copy.deepcopy(model)
        if self._scenario_can_execute(scenario, model):
            new_model = self._process_scenario(scenario, model)
            logger.info(f"Adding scenario {scenario.name}")
            logger.debug(f"model state:\n{new_model.get_status_text()}")
            self.out_suite.scenarios.append(scenario)
            return new_model
        if self._scenario_needs_refinement(scenario, model):
            if not self.flat_suite.scenarios:
                logger.debug("Refinement needed, but there are no scenarios left")
                self.flat_suite.scenarios.append(scenario)
                return False
            refinement_attempts_left = MAX_ATTEMPTS
            part1, part2 = self._split_refinement_candidate(scenario, model)
            exit_conditions = part2.steps[0].model_info['OUT']
            part2.steps[0].model_info['OUT'] = []
            part1.name = f"Partial {part1.name}"
            new_model = self._process_scenario(part1, model)
            logger.info(f"Adding partial scenario {scenario.name}")
            self.out_suite.scenarios.append(part1)
            while refinement_attempts_left:
                sub_scenario = random.choice(self.flat_suite.scenarios)
                self.flat_suite.scenarios.remove(sub_scenario)
                m_inserted = self._try_to_fit_in_scenario(sub_scenario, new_model)
                if m_inserted:
                    insert_valid_here = True
                    try:
                        for expr in exit_conditions:
                            if m_inserted.process_expression(expr) is False:
                                 insert_valid_here = False
                                 break
                    except Exception:
                        insert_valid_here = False
                    if insert_valid_here:
                        m_finished = self._try_to_fit_in_scenario(part2, m_inserted)
                        if m_finished:
                            return m_finished
                    else:
                        logger.debug(f"Scenario did not meet refinement conditions {exit_conditions}")
                    logger.info(f"Reconsidering {sub_scenario.name}, scenario excluded")
                    self.out_suite.scenarios.pop()
                refinement_attempts_left -=1
                self.flat_suite.scenarios.append(sub_scenario)
            self.out_suite.scenarios.remove(part1)
            
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
                            logger.debug(f"Refinement needed for scenario {scenario.name}")
                            return True
                    except Exception as err:
                        logger.debug(f"Refinement needed for scenario {scenario.name}")
                        return True
        return False

    @staticmethod
    def _split_refinement_candidate(scenario, model):
        m = copy.deepcopy(model)
        front = copy.deepcopy(scenario)
        front.steps = []
        back = copy.deepcopy(scenario)
        while back.steps:
            step = back.steps[0]
            if step.gherkin_kw in ['given', 'when']:
                for expr in step.model_info['IN']:
                    m.process_expression(expr)
            if step.gherkin_kw in ['when', 'then']:
                for expr in step.model_info['OUT']:
                    refine_here = False
                    try:
                        if m.process_expression(expr) is False:
                             refine_here = True
                    except Exception as err:
                        refine_here = True
                    if refine_here:
                        edge_step = Step('Log', scenario)
                        edge_step.args = (f"Refinement follows for step: {step.keyword}",)
                        edge_step.gherkin_kw = step.gherkin_kw
                        edge_step.model_info = dict(IN=step.model_info['IN'], OUT=[])
                        front.steps.append(edge_step)
                        edge_step = Step('Log', scenario)
                        edge_step.args = (f"Refinement completed for step: {step.keyword}",)
                        edge_step.gherkin_kw = step.gherkin_kw
                        edge_step.model_info = dict(IN=[], OUT=step.model_info['OUT'])
                        back.steps[0].model_info = dict(IN=[], OUT=[])
                        back.steps.insert(0, edge_step)
                        return front, back
            front.steps.append(back.steps.pop(0))
        assert False, "pop_steps_upto_refinement_point() called on non-refineable scenario"

    @staticmethod
    def _process_scenario(scenario, model):
        m = copy.deepcopy(model)
        for step in scenario.steps:
            for expr in SuiteProcessors._relevant_expressions(step):
                m.process_expression(expr)
        return m

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
                        logger.debug(f"Unable to insert scenario {scenario.name} due to step {step.keyword}: {expr} is False")
                        logger.debug(f"last state:\n{m.get_status_text()}")
                        return False
                except Exception as err:
                    logger.debug(f"Unable to insert scenario {scenario.name} due to step {step.keyword}: [{expr}] {err}")
                    logger.debug(f"last state:\n{m.get_status_text()}")
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
