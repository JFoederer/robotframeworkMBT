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

from typing import Any

from robot.api import logger
from robot.utils import is_list_like

from .modelspace import ModelSpace
from .steparguments import StepArgument, StepArguments, ArgKind
from .substitutionmap import SubstitutionMap
from .suitedata import Scenario, Step
from .tracestate import TraceState, TraceSnapShot


def try_to_fit_in_scenario(candidate: Scenario, tracestate: TraceState):
    """
    Tries to insert the candidate scenario into the trace (in full or partial) and
    updates tracestate accordingly.
    """
    model = tracestate.model if tracestate.model else ModelSpace()
    model.new_scenario_scope()
    inserted, remainder, extra_data = process_scenario(candidate, model)
    if not inserted:  # insertion failed
        tracestate.reject_scenario(candidate.src_id)
        logger.debug(extra_data['fail_msg'])
    elif not remainder:  # the scenario processed in full
        model.end_scenario_scope()
        tracestate.confirm_full_scenario(inserted.src_id, inserted, model)
        logger.debug(f"Inserted scenario {inserted.src_id}, {inserted.name}")
        if tracestate.is_refinement_active():
            handle_refinement_exit(inserted, tracestate)
    else:  # the scenario is split into two parts, ready for refinement
        logger.debug(f"Partially inserted scenario {inserted.src_id}, {inserted.name}\n"
                     f"Refinement needed at step: {remainder.steps[1]}")
        inserted.name = f"{inserted.name} (part {tracestate.highest_part(inserted.src_id)+1})"
        tracestate.push_partial_scenario(inserted.src_id, inserted, model, remainder)


def process_scenario(scenario: Scenario, model: ModelSpace) -> tuple[Scenario, Scenario, dict[str, Any]]:
    for step in scenario.steps:
        if 'error' in step.model_info:
            return None, None, dict(fail_masg=f"Error in scenario {scenario.name} "
                                    f"at step {step}: {step.model_info['error']}")
        for expr in _relevant_expressions(step):
            try:
                if model.process_expression(expr, step.args) is False:
                    if step.gherkin_kw in ['when', None] and expr in step.model_info['OUT']:
                        part1, part2 = split_for_refinement(scenario, step)
                        return part1, part2, dict()
                    else:
                        return None, None, dict(fail_msg=f"Unable to insert scenario {scenario.src_id}, "
                                                f"{scenario.name}, due to step '{step}': [{expr}] is False")
            except Exception as err:
                return None, None, dict(fail_msg=f"Unable to insert scenario {scenario.src_id}, "
                                        f"{scenario.name}, due to step '{step}': [{expr}] {err}")
    return scenario.copy(), None, dict()


def _relevant_expressions(step: Step) -> list[str]:
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


def split_for_refinement(scenario: Scenario, step: Step) -> tuple[Scenario, Scenario]:
    front, back = scenario.split_at_step(scenario.steps.index(step))
    remaining_steps = '\n\t'.join([step.full_keyword, '- '*35] + [s.full_keyword for s in back.steps[1:]])
    remaining_steps = _escape_robot_vars(remaining_steps)
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


def _escape_robot_vars(text: str) -> str:
    for seq in ("${", "@{", "%{", "&{", "*{"):
        text = text.replace(seq, "\\" + seq)
    return text


def handle_refinement_exit(inserted_refinement: Scenario, tracestate: TraceState):
    refinement_tail = tracestate.get_remainder(tracestate.active_refinements[-1])
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
        rewind(tracestate)  # Reject insterted scenario. Even though it fits, it is not a refinement.
        logger.debug(f"Reconsidering scenario {inserted_refinement.src_id}, {inserted_refinement.name}, "
                     f"did not meet refinement exit condition: {exit_conditions}")
        return

    model = tracestate.model
    tail_inserted, remainder, extra_data = process_scenario(refinement_tail, model)
    if not tail_inserted:
        logger.debug(extra_data['fail_msg'])
        # Confirm then rewind, to roll back complete scenario, including its refiements
        # Because that exit check passed, this is an error in the refined scenario itself
        tracestate.confirm_full_scenario(refinement_tail.src_id, refinement_tail, model)
        tail = rewind(tracestate)
        logger.debug(f"Having to roll back up to {tail.scenario.name if tail else 'the beginning'}")
    elif not remainder:
        model.end_scenario_scope()
        tracestate.confirm_full_scenario(tail_inserted.src_id, tail_inserted, model)
        logger.debug(f"Scenario '{tail_inserted.name}' completed after refinement")
        if tracestate.is_refinement_active():
            handle_refinement_exit(tail_inserted, tracestate)
    else:
        logger.debug(f"Partially inserted remainder of scenario {tail_inserted.src_id}, {tail_inserted.name}\n"
                     f"refinement needed at step: {remainder.steps[1]}")
        tail_inserted.name = f"{tail_inserted.name} (part {tracestate.highest_part(tail_inserted.src_id)+1})"
        tracestate.push_partial_scenario(tail_inserted.src_id, tail_inserted, model, remainder)


def generate_scenario_variant(scenario: Scenario, model: ModelSpace) -> Scenario:
    scenario = scenario.copy()
    # collect set of constraints
    subs = SubstitutionMap()
    try:
        for step in scenario.steps:
            for expr in step.model_info.get('MOD', []):
                modded_arg, constraint = _parse_modifier_expression(expr, step.args)
                if step.args[modded_arg].is_default:
                    continue
                if step.args[modded_arg].kind in [ArgKind.EMBEDDED, ArgKind.POSITIONAL, ArgKind.NAMED]:
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
                elif step.args[modded_arg].kind == ArgKind.VAR_POS:
                    if step.args[modded_arg].value:
                        modded_varargs = model.process_expression(constraint, step.args)
                        if not is_list_like(modded_varargs):
                            raise ValueError(f"Modifying varargs must yield a list of arguments")
                        # Varargs are not added to the substitution map, but are used directly as-is. A modifier can
                        # change the number of arguments in the list, making it impossible to decide which values to
                        # match and which to drop and/or duplicate.
                        step.args[modded_arg].value = modded_varargs
                elif step.args[modded_arg].kind == ArgKind.FREE_NAMED:
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
        logger.debug(f"Unable to insert scenario {scenario.src_id}, {scenario.name}, due to modifier\n"
                     f"    {err}: {subs}")
        return None

    # Update scenario with generated values
    if subs.solution:
        logger.debug(f"Example variant generated with argument substitution: {subs}")
    scenario.data_choices = subs
    for step in scenario.steps:
        if 'MOD' in step.model_info:
            for expr in step.model_info['MOD']:
                modded_arg, _ = _parse_modifier_expression(expr, step.args)
                if step.args[modded_arg].is_default:
                    continue
                org_example = step.args[modded_arg].org_value
                if step.args[modded_arg].kind in [ArgKind.EMBEDDED, ArgKind.POSITIONAL, ArgKind.NAMED]:
                    step.args[modded_arg].value = subs.solution[org_example]
    return scenario


def _parse_modifier_expression(expression: str, args: StepArguments) -> tuple[str, str]:
    if expression.startswith('${'):
        for var in args:
            if expression.casefold().startswith(var.arg.casefold()):
                assignment_expr = expression.replace(var.arg, '', 1).strip()
                if not assignment_expr.startswith('=') or assignment_expr.startswith('=='):
                    break  # not an assignment
                constraint = assignment_expr.replace('=', '', 1).strip()
                return var.arg, constraint
    raise ValueError(f"Invalid argument substitution: {expression}")


def rewind(tracestate: TraceState, drought_recovery: bool = False) -> TraceSnapShot | None:
    if tracestate[-1].remainder and tracestate.highest_part(tracestate[-1].remainder.src_id) > 1:
        # When rewinding an 'in between' part, rewind both the part and the refinement
        tracestate.rewind()
    tail = tracestate.rewind()
    while drought_recovery and tracestate.coverage_drought:
        tail = tracestate.rewind()
    return tail
