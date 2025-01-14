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
from robot.utils import is_list_like

from .substitutionmap import SubstitutionMap
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

        for id, scenario in enumerate(self.flat_suite.scenarios, start=1):
            scenario.src_id = id
        self.scenarios = self.flat_suite.scenarios[:]
        logger.debug("Use these numbers to reference scenarios from traces\n\t" +
                "\n\t".join([f"{s.src_id}: {s.name}" for s in self.scenarios]))

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
                        logger.debug(f"last state:\n{self.active_model.get_status_text()}")

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
        candidate = self._generate_scenario_variant(candidate, self.active_model)
        if not candidate:
            self.active_model.end_scenario_scope()
            self.tracestate.reject_scenario(index)
            self._report_tracestate_to_user()
            return False

        confirmed_candidate, new_model = self._process_scenario(candidate, self.active_model)
        if confirmed_candidate:
            self.active_model = new_model
            self.active_model.end_scenario_scope()
            self.tracestate.confirm_full_scenario(index, confirmed_candidate, self.active_model)
            logger.debug(f"Inserted scenario {confirmed_candidate.src_id}, {confirmed_candidate.name}")
            self._report_tracestate_to_user()
            logger.debug(f"last state:\n{self.active_model.get_status_text()}")
            return True

        part1, part2 = self._split_candidate_if_refinement_needed(candidate, self.active_model)
        if part2:
            exit_conditions = part2.steps[1].model_info['OUT']
            part1.name = f"{part1.name} (part {self.tracestate.highest_part(index)+1})"
            part1, new_model = self._process_scenario(part1, self.active_model)
            self.tracestate.push_partial_scenario(index, part1, new_model)
            self.active_model = new_model
            self._report_tracestate_to_user()
            logger.debug(f"last state:\n{self.active_model.get_status_text()}")

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
                        # Check exit condition before finalizing refinement and inserting the tail part
                        model_scratchpad = self.active_model.copy()
                        for expr in exit_conditions:
                            if model_scratchpad.process_expression(expr, part2.steps[1].emb_args) is False:
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
                        logger.debug(f"last state:\n{self.active_model.get_status_text()}")
                    logger.debug(f"Reconsidering {self.scenarios[i_refine].name}, scenario excluded")
                    self._rewind()
                    self._report_tracestate_to_user()
                i_refine = self.tracestate.next_candidate(retry=retry_flag)
            self._rewind()
            self._report_tracestate_to_user()
            return False

        self.active_model.end_scenario_scope()
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
                        if m.process_expression(expr, step.emb_args) is False:
                            return no_split
                    except Exception:
                        return no_split
            if step.gherkin_kw in ['when', 'then']:
                for expr in step.model_info['OUT']:
                    refine_here = False
                    try:
                        if m.process_expression(expr, step.emb_args) is False:
                            if step.gherkin_kw == 'when':
                                logger.debug(f"Refinement needed for scenario: {scenario.name}\nat step: {step}")
                                refine_here = True
                            else:
                                return no_split
                    except Exception:
                        return no_split
                    if refine_here:
                        front, back = scenario.split_at_step(scenario.steps.index(step))
                        edge_step = Step('Log', f"Refinement follows for step: {step}", parent=scenario)
                        edge_step.gherkin_kw = step.gherkin_kw
                        edge_step.model_info = dict(IN=step.model_info['IN'], OUT=[])
                        edge_step.emb_args = StepArguments(step.emb_args)
                        front.steps.append(edge_step)
                        edge_step = Step('Log', f"Refinement completed for step: {step}", parent=scenario)
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
                logger.debug(f"Error in scenario {scenario.name} at step {step}: {step.model_info['error']}")
                return None, None
            for expr in SuiteProcessors._relevant_expressions(step):
                try:
                    if m.process_expression(expr, step.emb_args) is False:
                        raise Exception(False)
                except Exception as err:
                    logger.debug(f"Unable to insert scenario {scenario.src_id}, {scenario.name}, "
                                 f"due to step '{step}': [{expr}] {err}")
                    return None, None
        return scenario, m

    @staticmethod
    def _relevant_expressions(step):
        expressions = []
        if 'IN' not in step.model_info or 'OUT' not in step.model_info:
            raise Exception(f"Model info incomplete for step: {step}")
        if step.gherkin_kw in ['given', 'when']:
            expressions += step.model_info['IN']
        if step.gherkin_kw in ['when', 'then']:
            expressions += step.model_info['OUT']
        return expressions

    def _generate_scenario_variant(self, scenario, model):
        m = model.copy()
        scenario = scenario.copy()
        scenarios_in_refinement = self.tracestate.find_scenarios_with_active_refinement()

        # reuse previous solution for all parts in split-up scenario
        for sir in scenarios_in_refinement:
            if sir.src_id == scenario.src_id:
                return scenario

        # collect set of constraints
        subs = SubstitutionMap()
        try:
            for step in scenario.steps:
                if 'MOD' in step.model_info:
                    for expr in step.model_info['MOD']:
                        modded_arg, constraint = self._parse_modifier_expression(expr, step.emb_args)
                        org_example = step.emb_args[modded_arg].org_value
                        if step.gherkin_kw == 'then':
                            constraint = None # No new constraints are processed for then-steps
                            if org_example not in subs.substitutions:
                                # if a then-step signals the first use of an example value, it is considered a new definition
                                subs.substitute(org_example, [org_example])
                                continue
                        if not constraint and org_example not in subs.substitutions:
                            raise ValueError(f"No options to choose from at first assignment to {org_example}")
                        if constraint and constraint != '.*':
                            options =  m.process_expression(constraint, step.emb_args)
                            if options == 'exec':
                                raise ValueError(f"Invalid constraint for argument substitution: {expr}")
                            if not options:
                                raise ValueError(f"Constraint on modifer did not yield any options: {expr}")
                            if not is_list_like(options):
                                raise ValueError(f"Constraint on modifer did not yield a set of options: {expr}")
                        else:
                            options = None
                        subs.substitute(org_example, options)
        except Exception as err:
            logger.debug(f"Unable to insert scenario {scenario.src_id}, {scenario.name}, due to modifier\n"
                         f"    In step {step}: {err}")
            return None

        try:
            subs.solve()
        except ValueError as err:
            logger.debug(f"Unable to insert scenario {scenario.src_id}, {scenario.name}, due to modifier\n    {err}: {subs}")
            return None

        # Update scenario with generated values
        if subs.solution:
            logger.debug(f"Example variant generated with argument substitution: {subs}")
        scenario.data_choices = subs
        for step in scenario.steps:
            if 'MOD' in step.model_info:
                for expr in step.model_info['MOD']:
                    modded_arg, constraint = self._parse_modifier_expression(expr, step.emb_args)
                    org_example = step.emb_args[modded_arg].org_value
                    step.emb_args[modded_arg].value = subs.solution[org_example]
        return scenario

    @staticmethod
    def _parse_modifier_expression(expression, args):
        if expression.startswith('${'):
            for var in args:
                if expression.casefold().startswith(var.arg.casefold()):
                    assignment_expr = expression.replace(var.arg, '', 1).strip()
                    if not assignment_expr.startswith('=') or assignment_expr.startswith('=='):
                        break # not an assignment
                    constraint = assignment_expr.replace('=', '', 1).strip()
                    return var.arg, constraint
        raise ValueError(f"Invalid argument substitution: {expression}")

    def _report_tracestate_to_user(self):
        user_trace = "["
        for snapshot in self.tracestate:
            part = f".{snapshot.id.split('.')[1]}" if '.' in snapshot.id else ""
            user_trace += f"{snapshot.scenario.src_id}{part}, "
        user_trace = user_trace[:-2] + "]" if ',' in user_trace else "[]"
        reject_trace = [self.scenarios[i].src_id for i in self.tracestate.tried]
        logger.debug(f"Trace: {user_trace} Reject: {reject_trace}")

    def _report_tracestate_wrapup(self):
        logger.info("Trace composed:")
        for step in self.tracestate:
            logger.info(step.scenario.name)
            logger.debug(f"model\n{step.model.get_status_text()}\n")
