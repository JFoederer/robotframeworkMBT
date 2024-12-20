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
import random

from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import not_keyword
from robot.api import logger

from .modelspace import ModelSpace
from .suitedata import Suite, Scenario, Step
from .tracestate import TraceState
from .steparguments import StepArguments

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
        self._fail_on_step_errors(in_suite)
        self.flat_suite = self.flatten(in_suite)

        self.scenarios = self.flat_suite.scenarios[:]
        # a short trace without the need for repeating scenarios is preferred
        self.try_to_reach_full_coverage(allow_duplicate_scenarios=False)

        if not self.tracestate.coverage_reached():
            logger.debug("Direct trace not available. Allowing repetition of scenarios")
            self.try_to_reach_full_coverage(allow_duplicate_scenarios=True)
            if not self.tracestate.coverage_reached():
                raise Exception("Unable to compose a consistent suite")

        self.out_suite.scenarios = self.tracestate.get_trace()
        self._report_tracestate_wrapup()
        return self.out_suite

    def try_to_reach_full_coverage(self, allow_duplicate_scenarios):
        random.shuffle(self.scenarios)
        self.tracestate = TraceState(len(self.scenarios))
        self.active_model = ModelSpace()
        self._init_reporting()

        while not self.tracestate.coverage_reached():
            i_candidate = self.tracestate.next_candidate(retry=allow_duplicate_scenarios)
            if i_candidate is None:
                if not self.tracestate.can_rewind():
                    break
                tail = self._rewind()
                logger.debug("Having to roll back up to "
                            f"{tail.scenario.name if tail else 'the beginning'}")
                self._report_tracestate_to_user()
            else:
                self.active_model.new_scenario_scope()
                inserted = self._try_to_fit_in_scenario(i_candidate, self._scenario_with_repeat_counter(i_candidate),
                                                        retry_flag=allow_duplicate_scenarios)
                if inserted:
                    self.DROUGHT_LIMIT = 50
                    if self.__last_candidate_changed_nothing():
                        logger.debug("Repeated scenario did not change the model's state. Stop trying.")
                        self._rewind()
                    elif self.tracestate.coverage_drought > self.DROUGHT_LIMIT:
                        logger.debug(f"Went too long without new coverage (>{self.DROUGHT_LIMIT}x). "
                                     "Roll back to last coverage increase and try something else.")
                        self._rewind(self.DROUGHT_LIMIT+1)
                        self._report_tracestate_to_user()

    def __last_candidate_changed_nothing(self):
        if len(self.tracestate) < 2:
            return False
        if self.tracestate[-1].id != self.tracestate[-2].id:
            return False
        return self.tracestate[-1].model == self.tracestate[-2].model

    def _scenario_with_repeat_counter(self, index):
        """Fetches the scenario by index and, if this scenario is already used in the trace,
        adds a repetition counter to its name."""
        candidate = self.scenarios[index]
        rep_count = self.tracestate.count(index)
        if rep_count:
            candidate = candidate.copy()
            candidate.name = f"{candidate.name} (rep {rep_count+1})"
        return candidate

    @staticmethod
    def _fail_on_step_errors(suite):
        error_list = suite.steps_with_errors()
        if error_list:
            err_msg = "Steps with errors in their model info found:\n"
            err_msg += '\n'.join([f"{s.keyword} [{s.model_info['error']}] used in {s.parent.name}"
                                      for s in error_list])
            raise Exception(err_msg)

    def _try_to_fit_in_scenario(self, index, candidate, retry_flag):
        confirmed_candidate, new_model = self._process_scenario(candidate, self.active_model)
        if confirmed_candidate:
            self.active_model = new_model
            self.active_model.end_scenario_scope()
            self.tracestate.confirm_full_scenario(index, confirmed_candidate, self.active_model)
            self._report_tracestate_to_user()
            return True

        part1, part2 = self._split_candidate_if_refinement_needed(candidate, self.active_model)
        if part2:
            exit_conditions = part2.steps[0].model_info['OUT']
            part1.name = f"{part1.name} (part {self.tracestate.highest_part(index)+1})"
            part1, new_model = self._process_scenario(part1, self.active_model)
            self.tracestate.push_partial_scenario(index, part1, new_model)
            self.active_model = new_model
            self._report_tracestate_to_user()

            i_refine = self.tracestate.next_candidate(retry=retry_flag)
            if i_refine is None:
                logger.debug("Refinement needed, but there are no scenarios left")
                self._rewind()
                self._report_tracestate_to_user()
                return False
            while i_refine is not None:
                self.active_model.new_scenario_scope()
                m_inserted = self._try_to_fit_in_scenario(i_refine, self._scenario_with_repeat_counter(i_refine), retry_flag)
                if m_inserted:
                    insert_valid_here = True
                    try:
                        for expr in exit_conditions:
                            if self.process_expression_incl_arg_subst(self.active_model, expr, part2.steps[0]) is False:
                                 insert_valid_here = False
                                 break
                    except Exception:
                        insert_valid_here = False
                    if insert_valid_here:
                        m_finished = self._try_to_fit_in_scenario(index, part2, retry_flag)
                        if m_finished:
                            return True
                    else:
                        logger.debug(f"Scenario did not meet refinement conditions {exit_conditions}")
                    logger.debug(f"Reconsidering {self.scenarios[i_refine].name}, scenario excluded")
                    self._rewind()
                    self._report_tracestate_to_user()
                i_refine = self.tracestate.next_candidate(retry=retry_flag)
            self._rewind()
            self._report_tracestate_to_user()
            return False

        self.tracestate.reject_scenario(index)
        self._report_tracestate_to_user()
        return False

    def _rewind(self, n=1):
        for i in range(n):
            tail = self.tracestate.rewind()
        self.active_model = self.tracestate.model or ModelSpace()
        return tail

    @staticmethod
    def _split_candidate_if_refinement_needed(scenario, model):
        m = model.copy()
        scenario = scenario.copy()
        no_split = (scenario, None)
        for step in scenario.steps:
            if 'error' in step.model_info:
                return no_split
            if step.gherkin_kw in ['given', 'when']:
                for expr in step.model_info['IN']:
                    try:
                        if SuiteProcessors.process_expression_incl_arg_subst(m, expr, step.emb_args) is False:
                            return no_split
                    except Exception:
                        return no_split
            if step.gherkin_kw in ['when', 'then']:
                for expr in step.model_info['OUT']:
                    refine_here = False
                    try:
                        if SuiteProcessors.process_expression_incl_arg_subst(m, expr, step.emb_args) is False:
                            logger.debug(f"Refinement needed for scenario: {scenario.name}\nat step: {step.keyword}")
                            if step.gherkin_kw == 'when':
                                refine_here = True
                            else:
                                return no_split
                    except Exception:
                        return no_split
                    if refine_here:
                        front, back = scenario.split_at_step(scenario.steps.index(step))
                        edge_step = Step('Log', f"Refinement follows for step: {step.keyword}", parent=scenario)
                        edge_step.gherkin_kw = step.gherkin_kw
                        edge_step.model_info = dict(IN=step.model_info['IN'], OUT=[])
                        edge_step.emb_args = StepArguments(step.emb_args)
                        front.steps.append(edge_step)
                        edge_step = Step('Log', f"Refinement completed for step: {step.keyword}", parent=scenario)
                        edge_step.model_info = dict(IN=[], OUT=[])
                        back.steps.insert(0, edge_step)
                        back.steps[1] = back.steps[1].copy()
                        back.steps[1].model_info['IN'] = []
                        return (front, back)
        return no_split

    @staticmethod
    def _process_scenario(scenario, model):
        m = model.copy()
        scenario = scenario.copy()
        for step in scenario.steps:
            if 'error' in step.model_info:
                logger.debug(f"Error in scenario {scenario.name} at step {step.keyword}: {step.model_info['error']}")
                return None, None
            for expr in SuiteProcessors._relevant_expressions(step):
                try:
                    if SuiteProcessors.process_expression_incl_arg_subst(m, expr, step.emb_args) is False:
                        raise Exception(False)
                except Exception as err:
                    logger.debug(f"Unable to insert scenario {scenario.name} due to step {step.keyword}: [{expr}] {err}")
                    logger.debug(f"last state:\n{m.get_status_text()}")
                    return None, None
        return scenario, m

    @staticmethod
    def process_expression_incl_arg_subst(model, expr, args):
        modded_arg, new_value = model.argument_modified_by_expression(expr, args)
        if modded_arg:
            args[modded_arg].value = new_value
            return True
        return model.process_expression(expr, args)

    @staticmethod
    def _relevant_expressions(step):
        expressions = []
        if 'IN' not in step.model_info or 'OUT' not in step.model_info:
            raise Exception(f"Model info incomplete for step: {step.keyword}")
        if step.gherkin_kw in ['given', 'when']:
            expressions += step.model_info['IN']
        if step.gherkin_kw in ['when', 'then']:
            expressions += step.model_info['OUT']
        return expressions

    def _init_reporting(self):
        self.shufflemap = [self.flat_suite.scenarios.index(s)+1 for s in self.scenarios]
        logger.debug("Use these numbers to reference scenarios from traces\n\t" +
                     "\n\t".join([f"{i+1}: {s.name}" for i, s in enumerate(self.flat_suite.scenarios)]))

    def _report_tracestate_to_user(self):
        user_trace = "["
        for id in [s.id for s in self.tracestate]:
            index = int(id.split('.')[0])
            part = f".{id.split('.')[1]}" if '.' in id else ""
            user_trace += f"{self.shufflemap[index]}{part}, "
        user_trace = user_trace[:-2] + "]" if ',' in user_trace else "[]"
        reject_trace = [self.shufflemap[i] for i in self.tracestate.tried]
        logger.debug(f"Trace: {user_trace} Reject: {reject_trace}")

    def _report_tracestate_wrapup(self):
        logger.info("Trace composed:")
        for step in self.tracestate:
            logger.info(step.scenario.name)
            logger.debug(f"model\n{step.model.get_status_text()}\n")
