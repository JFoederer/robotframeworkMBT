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

from robot.api import logger
from robot.utils import is_list_like

from .substitutionmap import SubstitutionMap
from .modelspace import ModelSpace
from .suitedata import Suite, Scenario, Step
from .tracestate import TraceState
from .steparguments import StepArgument, StepArguments


class SuiteProcessors:
    def echo(self, in_suite):
        return in_suite

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

    def process_test_suite(self, in_suite, *, seed='new'):
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

        self._init_randomiser(seed)
        self.shuffled = [s.src_id for s in self.scenarios]
        random.shuffle(self.shuffled)  # Keep a single shuffle for all TraceStates (non-essential)

        # a short trace without the need for repeating scenarios is preferred
        tracestate = self._try_to_reach_full_coverage(allow_duplicate_scenarios=False)

        if not tracestate.coverage_reached():
            logger.debug("Direct trace not available. Allowing repetition of scenarios")
            tracestate = self._try_to_reach_full_coverage(allow_duplicate_scenarios=True)
            if not tracestate.coverage_reached():
                raise Exception("Unable to compose a consistent suite")

        self.out_suite.scenarios = tracestate.get_trace()
        self._report_tracestate_wrapup(tracestate)
        return self.out_suite

    def _try_to_reach_full_coverage(self, allow_duplicate_scenarios):
        tracestate = TraceState(self.shuffled)
        refinement_stack = []
        while not tracestate.coverage_reached():
            candidate_id = tracestate.next_candidate(retry=allow_duplicate_scenarios)
            if candidate_id is None:  # No more candidates remaining for this level
                if not tracestate.can_rewind():
                    break
                tail = self._rewind(tracestate)
                logger.debug(f"Having to roll back up to {tail.scenario.name if tail else 'the beginning'}")
                self._report_tracestate_to_user(tracestate)
            else:
                candidate = self._select_scenario_variant(candidate_id, tracestate)
                if not candidate:  # No valid variant available in the current state
                    tracestate.reject_scenario(candidate_id)
                    continue
                previous_len = len(tracestate)
                self._try_to_fit_in_scenario(candidate, tracestate, refinement_stack)
                if len(tracestate) > previous_len:
                    self.DROUGHT_LIMIT = 50
                    if self.__last_candidate_changed_nothing(tracestate):
                        logger.debug("Repeated scenario did not change the model's state. Stop trying.")
                        self._rewind(tracestate)
                    elif tracestate.coverage_drought > self.DROUGHT_LIMIT:
                        logger.debug(f"Went too long without new coverage (>{self.DROUGHT_LIMIT}x). "
                                     "Roll back to last coverage increase and try something else.")
                        self._rewind(tracestate, drought_recovery=True)
                        self._report_tracestate_to_user(tracestate)
                        logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
        return tracestate

    @staticmethod
    def __last_candidate_changed_nothing(tracestate):
        if len(tracestate) < 2:
            return False
        if tracestate[-1].id != tracestate[-2].id:
            return False
        return tracestate[-1].model == tracestate[-2].model

    def _select_scenario_variant(self, candidate_id, tracestate):
        candidate = self._scenario_with_repeat_counter(candidate_id, tracestate)
        scenarios_in_refinement = tracestate.find_scenarios_with_active_refinement()
        if candidate_id in [s.src_id for s in scenarios_in_refinement]:
            # reuse previous solution for all parts in split-up scenario
            candidate = candidate.copy()
            candidate.data_choices = scenarios_in_refinement[candidate_id].data_choices.copy()
        else:
            candidate = self._generate_scenario_variant(candidate, tracestate.model or ModelSpace())
        return candidate

    def _scenario_with_repeat_counter(self, index, tracestate):
        """
        Fetches the scenario by index and, if this scenario is already
        used in the trace, adds a repetition counter to its name.
        """
        candidate = next(s for s in self.scenarios if s.src_id == index)
        rep_count = tracestate.count(index)
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

    def _try_to_fit_in_scenario(self, candidate, tracestate, refinement_stack):
        """
        Tries to insert the candidate scenario into the trace (in full or partial) and
        updates tracestate and refinement_stack accordingly.
        """
        model = tracestate.model if tracestate.model else ModelSpace()
        model.new_scenario_scope()
        inserted, remainder, new_model, extra_data = self._process_scenario(candidate, model)
        if not inserted:  # insertion failed
            model.end_scenario_scope()  # redundant??
            tracestate.reject_scenario(candidate.src_id)
            logger.debug(extra_data['fail_msg'])
            self._report_tracestate_to_user(tracestate)
        elif not remainder:  # the scenario processed in full
            new_model.end_scenario_scope()
            tracestate.confirm_full_scenario(inserted.src_id, inserted, new_model)
            logger.debug(f"Inserted scenario {inserted.src_id}, {inserted.name}")
            if refinement_stack:
                self._handle_refinement_exit(inserted, tracestate, refinement_stack)
            self._report_tracestate_to_user(tracestate)
            logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
        else:  # the scenario is split into two parts, ready for refinement
            logger.debug(f"Partially inserted scenario {inserted.src_id}, {inserted.name}\n"
                         f"Refinement needed at step: {remainder.steps[1]}")
            inserted.name = f"{inserted.name} (part {tracestate.highest_part(inserted.src_id)+1})"
            tracestate.push_partial_scenario(inserted.src_id, inserted, new_model)
            refinement_stack.append(remainder)
            self._report_tracestate_to_user(tracestate)
            logger.debug(f"last state:\n{new_model.get_status_text()}")

    def _handle_refinement_exit(self, inserted_refinement, tracestate, refinement_stack):
        refinement_tail = refinement_stack.pop()
        exit_conditions = refinement_tail.steps[1].model_info['OUT']
        exit_conditions_processed = False
        for expr in exit_conditions:
            try:
                if tracestate.model.process_expression(expr, refinement_tail.steps[1].args) is False:
                    break
            except Exception:
                break
        else:
            exit_conditions_processed = True

        if not exit_conditions_processed:
            self._rewind(tracestate)  # Reject insterted scenario. Even though it fits, it is not a refinement.
            refinement_stack.append(refinement_tail)
            logger.debug(f"Reconsidering scenario {inserted_refinement.src_id}, {inserted_refinement.name}, "
                         f"did not meet refinement conditions: {exit_conditions}")
            return

        tail_inserted, remainder, new_model, extra_data = self._process_scenario(refinement_tail, tracestate.model)
        if not tail_inserted:
            logger.debug(extra_data['fail_msg'])
            # Confirm then rewind, to roll back complete scenario, including its refiements
            # Because that exit check passed, this is an error in the refined scenario itself
            tracestate.confirm_full_scenario(refinement_tail.src_id, refinement_tail, new_model)
            tail = self._rewind(tracestate)
            logger.debug(f"Having to roll back up to {tail.scenario.name if tail else 'the beginning'}")
        elif not remainder:
            new_model.end_scenario_scope()
            tracestate.confirm_full_scenario(tail_inserted.src_id, tail_inserted, new_model)
            logger.debug(f"Scenario '{tail_inserted.name}' completed after refinement")
            if refinement_stack:
                self._handle_refinement_exit(tail_inserted, tracestate, refinement_stack)
        else:
            logger.debug(f"Partially inserted remainder of scenario {tail_inserted.src_id}, {tail_inserted.name}\n"
                         f"refinement needed at step: {remainder.steps[1]}")
            tail_inserted.name = f"{tail_inserted.name} (part {tracestate.highest_part(tail_inserted.src_id)+1})"
            tracestate.push_partial_scenario(tail_inserted.src_id, tail_inserted, new_model)
            refinement_stack.append(remainder)

    @staticmethod
    def _split_for_refinement(scenario, step):
        front, back = scenario.split_at_step(scenario.steps.index(step))
        remaining_steps = '\n\t'.join([step.full_keyword, '- '*35] + [s.full_keyword for s in back.steps[1:]])
        remaining_steps = SuiteProcessors._escape_robot_vars(remaining_steps)
        edge_step = Step('Log', f"Refinement follows for step:\n\t{remaining_steps}", parent=scenario)
        edge_step.gherkin_kw = step.gherkin_kw
        edge_step.model_info = dict(IN=step.model_info['IN'], OUT=[])
        edge_step.detached = True
        edge_step.args = StepArguments(step.args)
        front.steps.append(edge_step)
        back.steps.insert(0, Step('Log', f"Refinement ready, completing step", parent=scenario))
        back.steps[1] = back.steps[1].copy()
        back.steps[1].model_info['IN'] = []
        return (front, back)

    def _rewind(self, tracestate, drought_recovery=False):
        # Todo: Rewind needs to consider refinement stack.
        tail = tracestate.rewind()
        while drought_recovery and tracestate.coverage_drought:
            tail = tracestate.rewind()
        return tail

    @staticmethod
    def _escape_robot_vars(text):
        for seq in ("${", "@{", "%{", "&{", "*{"):
            text = text.replace(seq, "\\" + seq)
        return text

    @staticmethod
    def _process_scenario(scenario, model):
        m = model.copy()
        for step in scenario.steps:
            if 'error' in step.model_info:
                return None, None, m, dict(fail_masg=f"Error in scenario {scenario.name} "
                                           f"at step {step}: {step.model_info['error']}")
            for expr in SuiteProcessors._relevant_expressions(step):
                try:
                    if m.process_expression(expr, step.args) is False:
                        if step.gherkin_kw in ['when', None] and expr in step.model_info['OUT']:
                            part1, part2 = SuiteProcessors._split_for_refinement(scenario, step)
                            return part1, part2, m, dict()
                        else:
                            return None, None, m, dict(fail_msg=f"Unable to insert scenario {scenario.src_id}, "
                                                       f"{scenario.name}, due to step '{step}': [{expr}] is False")
                except Exception as err:
                    return None, None, m, dict(fail_msg=f"Unable to insert scenario {scenario.src_id}, {scenario.name},"
                                               f" due to step '{step}': [{expr}] {err}")
        return scenario.copy(), None, m, dict()

    @staticmethod
    def _relevant_expressions(step):
        if step.gherkin_kw is None and not step.model_info:
            return []  # model info is optional for action keywords
        expressions = []
        if 'IN' not in step.model_info or 'OUT' not in step.model_info:
            raise Exception(f"Model info incomplete for step: {step}")
        if step.gherkin_kw in ['given', 'when', None]:
            expressions += step.model_info['IN']
        if step.gherkin_kw in ['when', 'then', None]:
            expressions += step.model_info['OUT']
        return expressions

    def _generate_scenario_variant(self, scenario, model):
        scenario = scenario.copy()
        # collect set of constraints
        subs = SubstitutionMap()
        try:
            for step in scenario.steps:
                if 'MOD' in step.model_info:
                    for expr in step.model_info['MOD']:
                        modded_arg, constraint = self._parse_modifier_expression(expr, step.args)
                        if step.args[modded_arg].is_default:
                            continue
                        if step.args[modded_arg].kind in [StepArgument.EMBEDDED, StepArgument.POSITIONAL, StepArgument.NAMED]:
                            org_example = step.args[modded_arg].org_value
                            if step.gherkin_kw == 'then':
                                constraint = None  # No new constraints are processed for then-steps
                                if org_example not in subs.substitutions:
                                    # if a then-step signals the first use of an example value, it is considered a new definition
                                    subs.substitute(org_example, [org_example])
                                    continue
                            if not constraint and org_example not in subs.substitutions:
                                raise ValueError(f"No options to choose from at first assignment to {org_example}")
                            if constraint and constraint != '.*':
                                options = model.process_expression(constraint, step.args)
                                if options == 'exec':
                                    raise ValueError(f"Invalid constraint for argument substitution: {expr}")
                                if not options:
                                    raise ValueError(f"Constraint on modifer did not yield any options: {expr}")
                                if not is_list_like(options):
                                    raise ValueError(f"Constraint on modifer did not yield a set of options: {expr}")
                            else:
                                options = None
                            subs.substitute(org_example, options)
                        elif step.args[modded_arg].kind == StepArgument.VAR_POS:
                            if step.args[modded_arg].value:
                                modded_varargs = model.process_expression(constraint, step.args)
                                if not is_list_like(modded_varargs):
                                    raise ValueError(f"Modifying varargs must yield a list of arguments")
                                # Varargs are not added to the substitution map, but are used directly as-is. A modifier can
                                # change the number of arguments in the list, making it impossible to decide which values to
                                # match and which to drop and/or duplicate.
                                step.args[modded_arg].value = modded_varargs
                        elif step.args[modded_arg].kind == StepArgument.FREE_NAMED:
                            if step.args[modded_arg].value:
                                modded_free_args = model.process_expression(constraint, step.args)
                                if not isinstance(modded_free_args, dict):
                                    raise ValueError("Modifying free named arguments must yield a dict")
                                # Similar to varargs, modified free named arguments are used directly as-is.
                                step.args[modded_arg].value = modded_free_args
                        else:
                            raise AssertionError(f"Unknown argument kind for {modded_arg}")
        except Exception as err:
            logger.debug(f"Unable to insert scenario {scenario.src_id}, {scenario.name}, due to modifier\n"
                         f"    In step {step}: {err}")
            return None

        try:
            subs.solve()
        except ValueError as err:
            logger.debug(
                f"Unable to insert scenario {scenario.src_id}, {scenario.name}, due to modifier\n    {err}: {subs}")
            return None

        # Update scenario with generated values
        if subs.solution:
            logger.debug(f"Example variant generated with argument substitution: {subs}")
        scenario.data_choices = subs
        for step in scenario.steps:
            if 'MOD' in step.model_info:
                for expr in step.model_info['MOD']:
                    modded_arg, _ = self._parse_modifier_expression(expr, step.args)
                    if step.args[modded_arg].is_default:
                        continue
                    org_example = step.args[modded_arg].org_value
                    if step.args[modded_arg].kind in [StepArgument.EMBEDDED, StepArgument.POSITIONAL, StepArgument.NAMED]:
                        step.args[modded_arg].value = subs.solution[org_example]
        return scenario

    @staticmethod
    def _parse_modifier_expression(expression, args):
        if expression.startswith('${'):
            for var in args:
                if expression.casefold().startswith(var.arg.casefold()):
                    assignment_expr = expression.replace(var.arg, '', 1).strip()
                    if not assignment_expr.startswith('=') or assignment_expr.startswith('=='):
                        break  # not an assignment
                    constraint = assignment_expr.replace('=', '', 1).strip()
                    return var.arg, constraint
        raise ValueError(f"Invalid argument substitution: {expression}")

    @staticmethod
    def _report_tracestate_to_user(tracestate):
        user_trace = f"[{', '.join(tracestate.id_trace)}]"
        logger.debug(f"Trace: {user_trace} Reject: {list(tracestate.tried)}")

    @staticmethod
    def _report_tracestate_wrapup(tracestate):
        logger.info("Trace composed:")
        for progression in tracestate:
            logger.info(progression.scenario.name)
            logger.debug(f"model\n{progression.model.get_status_text()}\n")

    @staticmethod
    def _init_randomiser(seed):
        if isinstance(seed, str):
            seed = seed.strip()
        if str(seed).lower() == 'none':
            logger.info(
                f"Using system's random seed for trace generation. This trace cannot be rerun. Use `seed=new` to generate a reusable seed.")
        elif str(seed).lower() == 'new':
            new_seed = SuiteProcessors._generate_seed()
            logger.info(f"seed={new_seed} (use seed to rerun this trace)")
            random.seed(new_seed)
        else:
            logger.info(f"seed={seed} (as provided)")
            random.seed(seed)

    @staticmethod
    def _generate_seed():
        """Creates a random string of 5 words between 3 and 6 letters long"""
        vowels = ['a', 'e', 'i', 'o', 'u', 'y']
        consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                      'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']

        words = []
        for word in range(5):
            prior_choice = random.choice([vowels, consonants])
            last_choice = random.choice([vowels, consonants])
            string = random.choice(prior_choice) + random.choice(last_choice)  # add first two letters
            for letter in range(random.randint(1, 4)):                         # add 1 to 4 more letters
                if prior_choice is last_choice:
                    new_choice = consonants if prior_choice is vowels else vowels
                else:
                    new_choice = random.choice([vowels, consonants])
                prior_choice = last_choice
                last_choice = new_choice
                string += random.choice(new_choice)
            words.append(string)
        seed = '-'.join(words)
        return seed
