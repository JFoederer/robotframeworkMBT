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
        first_candidate = ts.next_candidate(retry=True)
        ts.confirm_full_scenario(first_candidate, 'one', {})
        ts.reject_scenario(ts.next_candidate(retry=True))
        ts.reject_scenario(ts.next_candidate(retry=True))
        retry_candidate = ts.next_candidate(retry=True)
        self.assertEqual(first_candidate, retry_candidate)
        ts.confirm_full_scenario(retry_candidate, 'one', {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), 'two', {})
        self.assertFalse(ts.coverage_reached())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), 'three', {})
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.get_trace(), ['one', 'one', 'two', 'three'])

    def test_retry_can_continue_once_coverage_is_reached(self):
        ts = TraceState(3)
        ts.confirm_full_scenario(ts.next_candidate(retry=True), 'one', {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), 'two', {})
        ts.confirm_full_scenario(ts.next_candidate(retry=True), 'three', {})
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.next_candidate(retry=True), 0)
        ts.reject_scenario(0)
        self.assertEqual(ts.next_candidate(retry=True), 1)
        self.assertEqual(ts.next_candidate(retry=False), None)

    def test_count_scenario_repetitions(self):
        ts = TraceState(2)
        first = ts.next_candidate()
        self.assertEqual(ts.count(first), 0)
        ts.confirm_full_scenario(first, 'one', {})
        self.assertEqual(ts.count(first), 1)
        ts.confirm_full_scenario(first, 'one', {})
        self.assertEqual(ts.count(first), 2)

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

    def test_model_property_takes_model_from_tail(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(ts.next_candidate(), 'one', dict(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), 'two', dict(b=2))
        self.assertEqual(ts.model, dict(b=2))
        ts.rewind()
        self.assertEqual(ts.model, dict(a=1))

    def test_no_model_from_empty_trace(self):
        ts = TraceState(1)
        self.assertIs(ts.model, None)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertIsNotNone(ts.model)
        ts.rewind()
        self.assertIs(ts.model, None)

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

    def test_adding_coverage_prevents_drought(self):
        ts = TraceState(3)
        ts.confirm_full_scenario(ts.next_candidate(), 'one', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(ts.next_candidate(), 'two', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(ts.next_candidate(), 'three', {})
        self.assertEqual(ts.coverage_drought, 0)

    def test_repeated_scenarios_increases_drought(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 2)

    def test_drought_is_reset_with_new_coverage(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(1, 'two', {})
        self.assertEqual(ts.coverage_drought, 0)

    def test_rewind_includes_drought_update(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(1, 'two', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.rewind()
        self.assertEqual(ts.coverage_drought, 1)
        ts.rewind()
        self.assertEqual(ts.coverage_drought, 0)

class TestPartialScenarios(unittest.TestCase):
    def test_push_partial_does_not_complete_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.coverage_reached(), False)

    def test_confirm_full_after_push_partial_completes_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, 'part2', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts.get_trace(), ['part1', 'part2', 'remainder'])
        self.assertIs(ts.coverage_reached(), True)

    def test_scenario_unavailble_once_pushed_partial(self):
        ts = TraceState(1)
        candidate = ts.next_candidate()
        ts.push_partial_scenario(candidate, 'part1', {})
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_of_single_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_all_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, 'part2', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.get_trace(), ['part1', 'part2'])
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.can_rewind(), False)

    def test_partial_scenario_still_excluded_from_candidacy_after_rewind(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.push_partial_scenario(0, 'part1', {})
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_to_partial_scenario(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', dict(a=1))
        ts.push_partial_scenario(0, 'part2', dict(b=2))
        snapshot = ts.rewind()
        self.assertEqual(snapshot.id, '0.1')
        self.assertEqual(snapshot.scenario, 'part1')
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_last_part(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one', dict(a=1))
        ts.push_partial_scenario(1, 'part1', dict(b=2))
        snapshot = ts.rewind()
        self.assertEqual(ts.get_trace(), ['one'])
        self.assertEqual(snapshot.id, '0')
        self.assertEqual(snapshot.scenario, 'one')
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_all_parts_of_completed_scenario_at_once(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', dict(a=1))
        ts.push_partial_scenario(0, 'part2', dict(b=2))
        ts.confirm_full_scenario(0, 'remainder', {})
        tail = ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(tail, None)

    def test_highest_part_after_first_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertEqual(ts[-1].id, '0.1')
        self.assertEqual(ts.highest_part(0), 1)

    def test_highest_part_after_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        ts.push_partial_scenario(0, 'part2', {})
        self.assertEqual(ts[-1].id, '0.2')
        self.assertEqual(ts.highest_part(0), 2)

    def test_highest_part_after_completing_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        ts.push_partial_scenario(0, 'part2', {})
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts[-1].id, '0.0')
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_after_partial_rewind(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        ts.push_partial_scenario(0, 'part2', {})
        self.assertEqual(ts.highest_part(0), 2)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 1)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_is_0_when_no_refinement_is_ongoing(self):
        ts = TraceState(1)
        self.assertEqual(ts.highest_part(0), 0)
        ts.push_partial_scenario(0, 'part1', {})
        ts.push_partial_scenario(0, 'part2', {})
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts.highest_part(0), 0)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_count_scenario_repetitions_with_partials(self):
        ts = TraceState(2)
        first = ts.next_candidate()
        self.assertEqual(ts.count(first), 0)
        ts.confirm_full_scenario(first, 'full', {})
        self.assertEqual(ts.count(first), 1)
        ts.push_partial_scenario(first, 'part1', {})
        ts.push_partial_scenario(first, 'part2', {})
        self.assertEqual(ts.count(first), 1)
        ts.confirm_full_scenario(first, 'remainder', {})
        self.assertEqual(ts.count(first), 2)
        second = ts.next_candidate()
        ts.push_partial_scenario(second, 'part1', {})
        self.assertEqual(ts.count(second), 0)
        ts.push_partial_scenario(second, 'part2', {})
        ts.confirm_full_scenario(second, 'remainder', {})
        self.assertEqual(ts.count(second), 1)

    def test_partial_scenario_is_tried_without_finishing(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {})
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (0,))

    def test_get_last_snapshot_by_index(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', dict(a=1))
        self.assertEqual(ts[-1].id, '0.1')
        self.assertEqual(ts[-1].scenario, 'part1')
        self.assertEqual(ts[-1].model, dict(a=1))
        self.assertEqual(ts[-1].coverage_drought, 0)
        ts.push_partial_scenario(0, 'part2', dict(b=2))
        ts.confirm_full_scenario(0, 'remainder', dict(c=3))
        self.assertEqual(ts[-1].id, '0.0')
        self.assertEqual(ts[-1].scenario, 'remainder')
        self.assertEqual(ts[-1].model, dict(c=3))
        self.assertEqual(ts[-1].coverage_drought, 0)

    def test_only_completed_scenarios_affect_drought(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one full', {})
        ts.push_partial_scenario(0, 'one part1', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(0, 'one remainder', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.push_partial_scenario(1, 'two part1', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(1, 'two remainder', {})
        self.assertEqual(ts.coverage_drought, 0)

class TestRefinement(unittest.TestCase):
    def test_single_step_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        candidate2 = ts.next_candidate()
        self.assertNotEqual(candidate1, candidate2)
        ts.confirm_full_scenario(candidate2, 'B1', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(candidate1, 'T1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T1.1', 'B1', 'T1.0'])

    def test_rewind_step_with_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, 'B1', {})
        ts.confirm_full_scenario(candidate1, 'T1.0', {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertEqual(ts.tried, (candidate1,))
        self.assertIs(ts.next_candidate(), candidate2)
        self.assertIs(ts.coverage_reached(), False)

    def test_rewind_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, 'B1', {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), ['T1.1'])
        self.assertEqual(ts.tried, (candidate2,))
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), False)

    def test_refinement_at_two_steps(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'T1.1', {})
        ts.confirm_full_scenario(ts.next_candidate(), 'B1', {})
        ts.push_partial_scenario(outer, 'T1.2', {})
        ts.confirm_full_scenario(ts.next_candidate(), 'B2', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, 'T1.0', {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T1.1', 'B1', 'T1.2', 'B2', 'T1.0'])

    def test_rewind_to_swap_refinements(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'T1.1', {})
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, 'B1', {})
        ts.push_partial_scenario(outer, 'T1.2', {})
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        self.assertEqual(ts.tried, (inner1,))
        self.assertEqual(ts.next_candidate(), inner2)
        ts.confirm_full_scenario(inner2, 'B2', {})
        ts.push_partial_scenario(outer, 'T1.2', {})
        self.assertEqual(ts.next_candidate(), inner1)
        ts.confirm_full_scenario(ts.next_candidate(), 'B1', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, 'T1.0', {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T1.1', 'B2', 'T1.2', 'B1', 'T1.0'])

    def test_rewind_partial_scenario_to_before_outer(self):
        ts = TraceState(4)
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, 'HEAD', {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'T1.1', {})
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, 'B1', {})
        ts.push_partial_scenario(outer, 'T1.2', {})
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        previous = ts.rewind()
        self.assertEqual(previous.scenario, 'HEAD')
        self.assertEqual(ts.get_trace(), ['HEAD'])
        self.assertNotIn(ts.next_candidate(), [head, outer])

    def test_rewind_scenario_with_double_refinement_as_one(self):
        ts = TraceState(4)
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, 'HEAD', {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'T1.1', {})
        ts.confirm_full_scenario(ts.next_candidate(), 'B1', {})
        ts.push_partial_scenario(outer, 'T1.2', {})
        ts.confirm_full_scenario(ts.next_candidate(), 'B2', {})
        ts.confirm_full_scenario(outer, 'T1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertEqual(previous.scenario, 'HEAD')
        self.assertEqual(ts.get_trace(), ['HEAD'])
        self.assertIs(ts.coverage_reached(), False)
        self.assertNotEqual(ts.next_candidate(), [head, outer])

    def test_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T1.1', {})
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M1.1', {})
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, 'B1', {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, 'M1.0', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, 'T1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T1.1', 'M1.1', 'B1', 'M1.0', 'T1.0'])

    def test_rewind_to_swap_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T1.1', {})
        lower_level = ts.next_candidate()
        ts.push_partial_scenario(lower_level, 'B1', {})
        middle_level = ts.next_candidate()
        ts.reject_scenario(middle_level)
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.next_candidate(), middle_level)
        ts.push_partial_scenario(middle_level, 'M1.1', {})
        ts.confirm_full_scenario(lower_level, 'B1', {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, 'M1.0', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, 'T1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T1.1', 'M1.1', 'B1', 'M1.0', 'T1.0'])

    def test_rewind_nested_refinement_as_one(self):
        ts = TraceState(4)
        ts.confirm_full_scenario(ts.next_candidate(), 'HEAD', {})
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T1.1', {})
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M1.1', {})
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, 'B1', {})
        ts.confirm_full_scenario(middle_level, 'M1.0', {})
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertIs(ts.next_candidate(), lower_level)
        self.assertIs(previous.scenario, 'T1.1')
        self.assertEqual(ts.get_trace(), ['HEAD', 'T1.1'])

    def test_rewind_scenario_with_nested_refinement_as_one(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T1.1', {})
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M1.1', {})
        ts.confirm_full_scenario(ts.next_candidate(), 'B1', {})
        ts.confirm_full_scenario(middle_level, 'M1.0', {})
        ts.confirm_full_scenario(top_level, 'T1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        previous = ts.rewind()
        self.assertIs(previous, None)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.get_trace(), [])
        self.assertEqual(ts.tried, (top_level,))

    def test_highest_parts_from_refined_scenario(self):
        ts = TraceState(4)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T1.1', {})
        middle_level_1 = ts.next_candidate()
        ts.push_partial_scenario(middle_level_1, 'M1.1', {})
        lower_level = ts.next_candidate()
        ts.push_partial_scenario(lower_level, 'B1.1', {})
        self.assertEqual(ts.highest_part(top_level), 1)
        self.assertEqual(ts.highest_part(middle_level_1), 1)
        self.assertEqual(ts.highest_part(lower_level), 1)
        ts.confirm_full_scenario(lower_level, 'B1.0', {})
        ts.confirm_full_scenario(middle_level_1, 'M1.0', {})
        ts.push_partial_scenario(top_level, 'T1.2', {})
        middle_level_2 = ts.next_candidate()
        ts.push_partial_scenario(middle_level_2, 'M2.1', {})
        ts.push_partial_scenario(middle_level_2, 'M2.2', {})
        ts.push_partial_scenario(middle_level_2, 'M2.3', {})
        self.assertEqual(ts.highest_part(top_level), 2)
        self.assertEqual(ts.highest_part(middle_level_1), 0)
        self.assertEqual(ts.highest_part(lower_level), 0)
        self.assertEqual(ts.highest_part(middle_level_2), 3)
        ts.confirm_full_scenario(middle_level_2, 'M2.0', {})
        self.assertEqual(ts.highest_part(middle_level_2), 0)
        self.assertEqual(ts.highest_part(top_level), 2)
        ts.confirm_full_scenario(top_level, 'T1.0', {})
        self.assertEqual(ts.highest_part(top_level), 0)
        self.assertEqual(ts.get_trace(), ['T1.1', 'M1.1', 'B1.1', 'B1.0', 'M1.0',
                                          'T1.2', 'M2.1', 'M2.2', 'M2.3', 'M2.0', 'T1.0'])

    def test_refinement_can_resolve_drought(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.confirm_full_scenario(candidate1, 'T1', {})
        ts.confirm_full_scenario(candidate1, 'T1', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        self.assertEqual(ts.coverage_drought, 1)
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, 'B1', {})
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(candidate1, 'T1.0', {})
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(candidate2, 'B1', {})
        self.assertEqual(ts.coverage_drought, 2)

    def test_scenario_cannot_refine_itself(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        candidate2 = ts.next_candidate()
        self.assertIsNotNone(candidate2)
        ts.reject_scenario(candidate2)
        self.assertIsNone(ts.next_candidate())

    def test_scenario_cannot_refine_itself_with_repetition(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate(retry=True)
        ts.push_partial_scenario(candidate1, 'T1.1', {})
        candidate2 = ts.next_candidate(retry=True)
        self.assertIsNotNone(candidate2)
        ts.reject_scenario(candidate2)
        self.assertIsNone(ts.next_candidate(retry=True))


if __name__ == '__main__':
    unittest.main()
