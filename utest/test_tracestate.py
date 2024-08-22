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

import unittest
from robotmbt.tracestate import TraceState
from robotmbt.suitedata import Scenario

class TestTraceState(unittest.TestCase):
    def test_an_empty_tracestate_doesnt_do_so_much(self):
        ts = TraceState(0)
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.can_rewind(), False)

    def test_completing_single_size_trace(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one'])

    def test_confirming_excludes_scenario_from_candidacy(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertIs(ts.next_candidate(), None)

    def test_trying_excludes_scenario_from_candidacy(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.reject_scenario(0)
        self.assertIs(ts.next_candidate(), None)

    def test_scenario_still_excluded_from_candidacy_after_rewind(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.confirm_full_scenario(0, 'one', {})
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_candidates_come_in_order_when_accepted(self):
        ts = TraceState(3)
        candidates = []
        for scenario in  range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [0, 1, 2, None])

    def test_candidates_come_in_order_when_rejected(self):
        ts = TraceState(3)
        candidates = []
        for _ in  range(3):
            candidates.append(ts.next_candidate())
            ts.reject_scenario(candidates[-1])
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [0, 1, 2, None])

    def test_rejected_scenarios_are_candidates_for_new_positions(self):
        ts = TraceState(3)
        candidates = []
        ts.reject_scenario(0)
        for scenario in  range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], scenario, {})
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [1, 0, 2, None])

    def test_previously_confirmed_scenarios_can_be_retried_if_no_new_candidates_exist(self):
        ts = TraceState(3)
        one = Scenario('one')
        two = Scenario('two')
        three = Scenario('three')
        first_candidate = ts.next_candidate(retry=True)
        ts.confirm_full_scenario(first_candidate, one, {})
        ts.reject_scenario(ts.next_candidate(retry=True))
        ts.reject_scenario(ts.next_candidate(retry=True))
        retry_candidate = ts.next_candidate(retry=True)
        self.assertEqual(first_candidate, retry_candidate)
        ts.confirm_full_scenario(retry_candidate, one, {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), two, {})
        self.assertFalse(ts.coverage_reached())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), three, {})
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.get_trace(), [one, one, two, three])

    def test_retry_can_continue_once_coverage_is_reached(self):
        ts = TraceState(3)
        one = Scenario('one')
        two = Scenario('two')
        three = Scenario('three')
        ts.confirm_full_scenario(ts.next_candidate(retry=True), one, {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), two, {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), three, {})
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.next_candidate(retry=True), 0)
        ts.reject_scenario(0)
        self.assertEqual(ts.next_candidate(retry=True), 1)
        self.assertEqual(ts.next_candidate(retry=False), None)

    def test_rewind_single_available_scenario(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertIs(ts.can_rewind(), False)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.next_candidate(), None)
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_returns_none_after_rewinding_last_step(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertIs(ts.rewind(), None)

    def test_traces_can_have_multiple_sceanrios(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'foo', dict(a=1))
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(1, 'bar', dict(b=2))
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['foo', 'bar'])

    def test_rewind_returns_snapshot_of_the_step_before(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'foo', dict(a=1))
        ts.confirm_full_scenario(1, 'bar', dict(b=2))
        tail = ts.rewind()
        self.assertEqual(tail.id, '0')
        self.assertEqual(tail.scenario, 'foo')
        self.assertEqual(tail.model, dict(a=1))

    def test_completing_size_three_trace(self):
        ts = TraceState(3)
        ts.confirm_full_scenario(ts.next_candidate(), 1, {})
        ts.confirm_full_scenario(ts.next_candidate(), 2, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(ts.next_candidate(), 3, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [1, 2, 3])

    def test_completing_size_three_trace_after_reject(self):
        ts = TraceState(3)
        first = ts.next_candidate()
        ts.confirm_full_scenario(first, first, {})
        rejected = ts.next_candidate()
        ts.reject_scenario(rejected)
        third = ts.next_candidate()
        ts.confirm_full_scenario(third, third, {})
        self.assertIs(ts.coverage_reached(), False)
        second = ts.next_candidate()
        self.assertEqual(rejected, second)
        ts.confirm_full_scenario(second, second, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [first, third, second])

    def test_completing_size_three_trace_after_rewind(self):
        ts = TraceState(3)
        first = ts.next_candidate()
        ts.confirm_full_scenario(first, first, {})
        reject2 = ts.next_candidate()
        ts.reject_scenario(reject2)
        reject3 = ts.next_candidate()
        ts.reject_scenario(reject3)
        self.assertEqual(len(ts.get_trace()), 1)
        ts.rewind()
        self.assertEqual(len(ts.get_trace()), 0)
        retry_first = ts.next_candidate()
        self.assertNotEqual(first, retry_first)
        ts.confirm_full_scenario(retry_first, retry_first, {})
        retry_second = ts.next_candidate()
        ts.confirm_full_scenario(retry_second, retry_second, {})
        retry_third = ts.next_candidate()
        ts.confirm_full_scenario(retry_third, retry_third, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [retry_first, retry_second, retry_third])

    def test_highest_part_when_index_not_present(self):
        ts = TraceState(1)
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_for_non_partial_sceanrio(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.highest_part(0), 0)

    def test_create_empty_modelspace_on_empty_trace(self):
        ts = TraceState(1)
        self.assertIn('ModelSpace', ts.model.__class__.__name__)
        self.assertEqual(dir(ts.model), [])

    def test_model__property_takes_model_from_tail(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(ts.next_candidate(), 'one', dict(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), 'two', dict(b=2))
        self.assertEqual(ts.model, dict(b=2))
        ts.rewind()
        self.assertEqual(ts.model, dict(a=1))

    def test_tried_property_starts_empty(self):
        ts = TraceState(1)
        self.assertEqual(ts.tried, ())

    def test_rejected_scenarios_are_tried(self):
        ts = TraceState(1)
        ts.reject_scenario(0)
        self.assertEqual(ts.tried, (0,))

    def test_confirmed_scenario_is_tried_and_triggers_next_step(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (0,))

    def test_can_iterate_over_tracestate_snapshots(self):
        ts = TraceState(3)
        ts.confirm_full_scenario(ts.next_candidate(), 'one', dict(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), 'two', dict(b=2))
        ts.confirm_full_scenario(ts.next_candidate(), 'three', dict(c=3))
        for act, exp in zip(ts, ['0', '1', '2']):
            self.assertEqual(act.id, exp)
        for act, exp in zip(ts, ['one', 'two', 'three']):
            self.assertEqual(act.scenario, exp)
        for act, exp in zip(ts, [dict(a=1), dict(b=2), dict(c=3)]):
            self.assertEqual(act.model, exp)

    def test_can_index_tracestate_snapshots(self):
        ts = TraceState(3)
        ts.confirm_full_scenario(ts.next_candidate(), 'one', dict(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), 'two', dict(b=2))
        ts.confirm_full_scenario(ts.next_candidate(), 'three', dict(c=3))
        self.assertEqual(ts[0].id, '0')
        self.assertEqual(ts[1].scenario, 'two')
        self.assertEqual(ts[2].model, dict(c=3))
        self.assertEqual(ts[-1].scenario, 'three')
        self.assertEqual([s.id for s in ts[1:]], ['1', '2'])


class TestPartialScenarios(unittest.TestCase):
    def setUp(self):
        self.scenario = Scenario('full')
        self.scenario.steps = ['part1', 'part2', 'remainder']
        self.part1, rest = self.scenario.split_at_step(1)
        self.part2, self.remainder = rest.split_at_step(1)
        # Confirm that the parts are not the same. Tests rely on that.
        self.assertEqual(len(set([self.part1, self.part2, self.remainder])), 3)

    def test_push_partial_does_not_complete_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertEqual(ts.get_trace(), [self.part1])
        self.assertIs(ts.coverage_reached(), False)

    def test_confirm_full_after_push_partial_completes_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, self.part2, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(0, self.remainder, {})
        self.assertEqual(ts.get_trace(), [self.part1, self.part2, self.remainder])
        self.assertIs(ts.coverage_reached(), True)

    def test_scenario_unavailble_once_pushed_partial(self):
        ts = TraceState(1)
        candidate = ts.next_candidate()
        ts.push_partial_scenario(candidate, self.part1, {})
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_of_single_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertEqual(ts.get_trace(), [self.part1])
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_all_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, self.part2, {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.get_trace(), [self.part1, self.part2])
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [self.part1])
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.can_rewind(), False)

    def test_partial_scenario_still_excluded_from_candidacy_after_rewind(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.push_partial_scenario(0, self.part1, {})
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_to_partial_scenario(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, dict(a=1))
        ts.push_partial_scenario(0, self.part2, dict(b=2))
        snapshot = ts.rewind()
        self.assertEqual(snapshot.id, '0.1')
        self.assertEqual(snapshot.scenario, self.part1)
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_last_part(self):
        ts = TraceState(2)
        one = Scenario('one')
        ts.confirm_full_scenario(0, one, dict(a=1))
        ts.push_partial_scenario(1, self.part1, dict(b=2))
        snapshot = ts.rewind()
        self.assertEqual(ts.get_trace(), [one])
        self.assertEqual(snapshot.id, '0')
        self.assertEqual(snapshot.scenario, one)
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_all_parts_of_completed_scenario_at_once(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, dict(a=1))
        ts.push_partial_scenario(0, self.part2, dict(b=2))
        ts.confirm_full_scenario(0, self.remainder, {})
        tail = ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(tail, None)

    def test_highest_part_after_first_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertEqual(ts[-1].id, '0.1')
        self.assertEqual(ts.highest_part(0), 1)

    def test_highest_part_after_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        ts.push_partial_scenario(0, self.part2, {})
        self.assertEqual(ts[-1].id, '0.2')
        self.assertEqual(ts.highest_part(0), 2)

    def test_highest_part_after_completing_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        ts.push_partial_scenario(0, self.part2, {})
        ts.confirm_full_scenario(0, self.remainder, {})
        self.assertEqual(ts[-1].id, '0.0')
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_after_partial_rewind(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        ts.push_partial_scenario(0, self.part2, {})
        self.assertEqual(ts.highest_part(0), 2)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 1)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_is_0_when_no_refinement_is_ongoing(self):
        ts = TraceState(1)
        self.assertEqual(ts.highest_part(0), 0)
        ts.push_partial_scenario(0, self.part1, {})
        ts.push_partial_scenario(0, self.part2, {})
        ts.confirm_full_scenario(0, self.remainder, {})
        self.assertEqual(ts.highest_part(0), 0)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_partial_scenario_is_tried_without_finishing(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, {})
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (0,))

    def test_get_last_snapshot_by_index(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, self.part1, dict(a=1))
        self.assertEqual(ts[-1].id, '0.1')
        self.assertEqual(ts[-1].scenario, self.part1)
        self.assertEqual(ts[-1].model, dict(a=1))
        ts.push_partial_scenario(0, self.part2, dict(b=2))
        ts.confirm_full_scenario(0, self.remainder, dict(c=3))
        self.assertEqual(ts[-1].id, '0.0')
        self.assertEqual(ts[-1].scenario, self.remainder)
        self.assertTrue(ts[-1].scenario.partial)
        self.assertEqual(ts[-1].model, dict(c=3))

class TestRefinement(unittest.TestCase):
    def setUp(self):
        self.top = Scenario('Top level')
        self.top.steps = ['T1', 'T2', 'T0']
        self.t1, self.t_rest = self.top.split_at_step(1)
        self.bottom = Scenario('Bottom level')
        self.bottom.steps = ['B1', 'B0']
        self.bottom2 = Scenario('Second bottom level scenario')
        self.mid = Scenario('Mid level')
        self.mid.steps = ['M1', 'M0']
        self.mid2 = Scenario('Second mid level scenario')

    def test_single_step_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, self.t1, {})
        candidate2 = ts.next_candidate()
        self.assertNotEqual(candidate1, candidate2)
        ts.confirm_full_scenario(candidate2, self.bottom, {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(candidate1, self.t_rest, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [self.t1, self.bottom, self.t_rest])

    def test_rewind_step_with_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, self.t1, {})
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, self.bottom, {})
        ts.confirm_full_scenario(candidate1, self.t_rest, {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertEqual(ts.tried, (candidate1,))
        self.assertIs(ts.next_candidate(), candidate2)
        self.assertIs(ts.coverage_reached(), False)

    def test_rewind_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, self.t1, {})
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, self.bottom, {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), [self.t1])
        self.assertEqual(ts.tried, (candidate2,))
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), False)

    def test_refinement_at_two_steps(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, self.t1, {})
        t2, remainder = self.t_rest.split_at_step(1)
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom, {})
        ts.push_partial_scenario(outer, t2, {})
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom2, {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, remainder, {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [self.t1, self.bottom, t2, self.bottom2, remainder])

    def test_rewind_to_swap_refinements(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, self.t1, {})
        t2, remainder = self.t_rest.split_at_step(1)
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, self.bottom, {})
        ts.push_partial_scenario(outer, t2, {})
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        self.assertEqual(ts.tried, (inner1,))
        self.assertEqual(ts.next_candidate(), inner2)
        ts.confirm_full_scenario(inner2, self.bottom2, {})
        ts.push_partial_scenario(outer, t2, {})
        self.assertEqual(ts.next_candidate(), inner1)
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom, {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, remainder, {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [self.t1, self.bottom2, t2, self.bottom, remainder])

    def test_rewind_partial_scenario_to_before_outer(self):
        ts = TraceState(4)
        head_scenario = Scenario('head')
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, head_scenario, {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, self.t1, {})
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, self.bottom, {})
        t2, _ = self.t_rest.split_at_step(1)
        ts.push_partial_scenario(outer, t2, {})
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        previous = ts.rewind()
        self.assertEqual(previous.scenario, head_scenario)
        self.assertEqual(ts.get_trace(), [head_scenario])
        self.assertNotIn(ts.next_candidate(), [head, outer])

    def test_rewind_scenario_with_double_refinement_as_one(self):
        ts = TraceState(4)
        head_scenario = Scenario('head')
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, head_scenario, {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, self.t1, {})
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom, {})
        t2, remainder = self.t_rest.split_at_step(1)
        ts.push_partial_scenario(outer, t2, {})
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom2, {})
        ts.confirm_full_scenario(outer, remainder, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertEqual(previous.scenario, head_scenario)
        self.assertEqual(ts.get_trace(), [head_scenario])
        self.assertIs(ts.coverage_reached(), False)
        self.assertNotEqual(ts.next_candidate(), [head, outer])

    def test_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, self.t1, {})
        middle_level = ts.next_candidate()
        m1, m_rest = self.mid.split_at_step(1)
        ts.push_partial_scenario(middle_level, m1, {})
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, self.bottom, {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, m_rest, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, self.t_rest, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [self.t1, m1, self.bottom, m_rest, self.t_rest])

    def test_rewind_to_swap_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, self.t1, {})
        lower_level = ts.next_candidate()
        ts.push_partial_scenario(lower_level, self.bottom, {})
        middle_level = ts.next_candidate()
        ts.reject_scenario(middle_level)
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.next_candidate(), middle_level)
        m1, m0 = self.mid.split_at_step(1)
        ts.push_partial_scenario(middle_level, m1, {})
        ts.confirm_full_scenario(lower_level, self.bottom, {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, m0, {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, self.t_rest, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [self.t1, m1, self.bottom, m0, self.t_rest])

    def test_rewind_nested_refinement_as_one(self):
        ts = TraceState(4)
        head_scenario = Scenario('head')
        ts.confirm_full_scenario(ts.next_candidate(), head_scenario, {})
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, self.t1, {})
        middle_level = ts.next_candidate()
        m1, m0 = self.mid.split_at_step(1)
        ts.push_partial_scenario(middle_level, m1, {})
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, self.bottom, {})
        ts.confirm_full_scenario(middle_level, m0, {})
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertIs(ts.next_candidate(), lower_level)
        self.assertIs(previous.scenario, self.t1)
        self.assertEqual(ts.get_trace(), [head_scenario, self.t1])

    def test_rewind_scenario_with_nested_refinement_as_one(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, self.t1, {})
        middle_level = ts.next_candidate()
        m1, m0 = self.mid.split_at_step(1)
        ts.push_partial_scenario(middle_level, m1, {})
        ts.confirm_full_scenario(ts.next_candidate(), self.bottom, {})
        ts.confirm_full_scenario(middle_level, m0, {})
        ts.confirm_full_scenario(top_level, self.t_rest, {})
        self.assertIs(ts.coverage_reached(), True)
        previous = ts.rewind()
        self.assertIs(previous, None)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.get_trace(), [])
        self.assertEqual(ts.tried, (top_level,))

    def test_highest_parts_from_refined_scenario(self):
        ts = TraceState(4)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, self.t1, {})
        t2, t0 = self.t_rest.split_at_step(1)
        middle_level_1 = ts.next_candidate()
        m11, m10 = self.mid.split_at_step(1)
        ts.push_partial_scenario(middle_level_1, m11, {})
        lower_level = ts.next_candidate()
        b1, b0 = self.bottom.split_at_step(1)
        ts.push_partial_scenario(lower_level, b1, {})
        self.assertEqual(ts.highest_part(top_level), 1)
        self.assertEqual(ts.highest_part(middle_level_1), 1)
        self.assertEqual(ts.highest_part(lower_level), 1)
        ts.confirm_full_scenario(lower_level, b0, {})
        ts.confirm_full_scenario(middle_level_1, m10, {})
        ts.push_partial_scenario(top_level, t2, {})
        middle_level_2 = ts.next_candidate()
        self.mid2.steps = ['M21', 'M22', 'M23', 'M0']
        m21, tmp = self.mid2.split_at_step(1)
        m22, tmp = tmp.split_at_step(1)
        m23, m20 = tmp.split_at_step(1)
        ts.push_partial_scenario(middle_level_2, m21, {})
        ts.push_partial_scenario(middle_level_2, m22, {})
        ts.push_partial_scenario(middle_level_2, m23, {})
        self.assertEqual(ts.highest_part(top_level), 2)
        self.assertEqual(ts.highest_part(middle_level_1), 0)
        self.assertEqual(ts.highest_part(lower_level), 0)
        self.assertEqual(ts.highest_part(middle_level_2), 3)
        ts.confirm_full_scenario(middle_level_2, m20, {})
        self.assertEqual(ts.highest_part(middle_level_2), 0)
        self.assertEqual(ts.highest_part(top_level), 2)
        ts.confirm_full_scenario(top_level, t0, {})
        self.assertEqual(ts.highest_part(top_level), 0)
        self.assertEqual(ts.get_trace(), [self.t1, m11, b1, b0, m10, t2, m21, m22, m23, m20, t0])

if __name__ == '__main__':
    unittest.main()
