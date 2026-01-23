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
        ts = TraceState([])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.can_rewind(), False)

    def test_completing_single_size_trace(self):
        ts = TraceState([1])
        self.assertEqual(ts.next_candidate(), 1)
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one'])

    def test_confirming_excludes_scenario_from_candidacy(self):
        ts = TraceState([1])
        self.assertEqual(ts.next_candidate(), 1)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertIs(ts.next_candidate(), None)

    def test_trying_excludes_scenario_from_candidacy(self):
        ts = TraceState([1])
        self.assertEqual(ts.next_candidate(), 1)
        ts.reject_scenario(1)
        self.assertIs(ts.next_candidate(), None)

    def test_scenario_still_excluded_from_candidacy_after_rewind(self):
        ts = TraceState([1])
        self.assertEqual(ts.next_candidate(), 1)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_candidates_come_in_order_when_accepted(self):
        ts = TraceState([10, 20, 30])
        candidates = []
        for _ in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], ScenarioStub(), ModelStub())
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [10, 20, 30, None])

    def test_scenarios_must_be_uniquely_identifiable(self):
        self.assertRaises(ValueError, TraceState, [1, 2, 3, 2])

    def test_candidates_come_in_order_when_rejected(self):
        ts = TraceState([10, 20, 30])
        candidates = []
        for _ in range(3):
            candidates.append(ts.next_candidate())
            ts.reject_scenario(candidates[-1])
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [10, 20, 30, None])

    def test_rejected_scenarios_are_candidates_for_new_positions(self):
        ts = TraceState([1, 2, 3])
        candidates = []
        ts.reject_scenario(1)
        for _ in range(3):
            candidates.append(ts.next_candidate())
            ts.confirm_full_scenario(candidates[-1], ScenarioStub(), ModelStub())
        candidates.append(ts.next_candidate())
        self.assertEqual(candidates, [2, 1, 3, None])

    def test_previously_confirmed_scenarios_can_be_retried_if_no_new_candidates_exist(self):
        ts = TraceState(range(3))
        first_candidate = ts.next_candidate(retry=True)
        ts.confirm_full_scenario(first_candidate, ScenarioStub('one'), ModelStub())
        ts.reject_scenario(ts.next_candidate(retry=True))
        ts.reject_scenario(ts.next_candidate(retry=True))
        retry_candidate = ts.next_candidate(retry=True)
        self.assertEqual(first_candidate, retry_candidate)
        ts.confirm_full_scenario(retry_candidate, ScenarioStub('one'), ModelStub())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), ScenarioStub('two'), ModelStub())
        self.assertFalse(ts.coverage_reached())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), ScenarioStub('three'), ModelStub())
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.get_trace(), ['one', 'one', 'two', 'three'])

    def test_retry_can_continue_once_coverage_is_reached(self):
        ts = TraceState([1, 2, 3])
        ts.confirm_full_scenario(ts.next_candidate(retry=True), ScenarioStub('one'), ModelStub())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), ScenarioStub('two'), ModelStub())
        ts.confirm_full_scenario(ts.next_candidate(retry=True), ScenarioStub('three'), ModelStub())
        self.assertTrue(ts.coverage_reached())
        self.assertEqual(ts.next_candidate(retry=True), 1)
        ts.reject_scenario(1)
        self.assertEqual(ts.next_candidate(retry=True), 2)
        self.assertEqual(ts.next_candidate(retry=False), None)

    def test_count_scenario_repetitions(self):
        ts = TraceState([1, 2])
        first = ts.next_candidate()
        self.assertEqual(ts.count(first), 0)
        ts.confirm_full_scenario(first, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.count(first), 1)
        ts.confirm_full_scenario(first, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.count(first), 2)

    def test_rewind_single_available_scenario(self):
        ts = TraceState([1])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertIs(ts.can_rewind(), False)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.next_candidate(), None)
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_returns_none_after_rewinding_last_step(self):
        ts = TraceState([1])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertIs(ts.rewind(), None)

    def test_traces_can_have_multiple_scenarios(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('foo'), ModelStub(a=1))
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(2, ScenarioStub('bar'), ModelStub(b=2))
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['foo', 'bar'])

    def test_rewind_returns_snapshot_of_the_step_before(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('foo'), ModelStub(a=1))
        ts.confirm_full_scenario(2, ScenarioStub('bar'), ModelStub(b=2))
        tail = ts.rewind()
        self.assertEqual(tail.id, '1')
        self.assertEqual(tail.scenario, 'foo')
        self.assertEqual(tail.model, dict(a=1))

    def test_completing_size_three_trace(self):
        ts = TraceState(range(3))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('one'), ModelStub())
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('two'), ModelStub())
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('three'), ModelStub())
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one', 'two', 'three'])

    def test_completing_size_three_trace_after_reject(self):
        ts = TraceState(range(3))
        first = ts.next_candidate()
        ts.confirm_full_scenario(first, ScenarioStub('one'), ModelStub())
        rejected = ts.next_candidate()
        ts.reject_scenario(rejected)
        third = ts.next_candidate()
        ts.confirm_full_scenario(third, ScenarioStub('three'), ModelStub())
        self.assertIs(ts.coverage_reached(), False)
        second = ts.next_candidate()
        self.assertEqual(rejected, second)
        ts.confirm_full_scenario(second, ScenarioStub('two'), ModelStub())
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one', 'three', 'two'])

    def test_completing_size_three_trace_after_rewind(self):
        ts = TraceState(range(3))
        first = ts.next_candidate()
        ts.confirm_full_scenario(first, ScenarioStub('one'), ModelStub())
        reject2 = ts.next_candidate()
        ts.reject_scenario(reject2)
        reject3 = ts.next_candidate()
        ts.reject_scenario(reject3)
        self.assertEqual(len(ts.get_trace()), 1)
        ts.rewind()
        self.assertEqual(len(ts.get_trace()), 0)
        retry_first = ts.next_candidate()
        self.assertNotEqual(first, retry_first)
        ts.confirm_full_scenario(retry_first, ScenarioStub('two'), ModelStub())
        retry_second = ts.next_candidate()
        ts.confirm_full_scenario(retry_second, ScenarioStub('one'), ModelStub())
        retry_third = ts.next_candidate()
        ts.confirm_full_scenario(retry_third, ScenarioStub('three'), ModelStub())
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['two', 'one', 'three'])

    def test_highest_part_when_index_not_present(self):
        ts = TraceState([1])
        self.assertEqual(ts.highest_part(1), 0)

    def test_highest_part_for_non_partial_sceanrio(self):
        ts = TraceState([1])
        ts.confirm_full_scenario(1, ScenarioStub(), ModelStub())
        self.assertEqual(ts.highest_part(1), 0)

    def test_model_property_takes_model_from_tail(self):
        ts = TraceState(range(2))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('one'), ModelStub(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('two'), ModelStub(b=2))
        self.assertEqual(ts.model, dict(b=2))
        ts.rewind()
        self.assertEqual(ts.model, dict(a=1))

    def test_no_model_from_empty_trace(self):
        ts = TraceState([1])
        self.assertIs(ts.model, None)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertIsNotNone(ts.model)
        ts.rewind()
        self.assertIs(ts.model, None)

    def test_tried_property_starts_empty(self):
        ts = TraceState([1])
        self.assertEqual(ts.tried, ())

    def test_rejected_scenarios_are_tried(self):
        ts = TraceState([1])
        ts.reject_scenario(1)
        self.assertEqual(ts.tried, (1,))

    def test_confirmed_scenario_is_tried_and_triggers_next_step(self):
        ts = TraceState([1])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (1,))

    def test_can_iterate_over_tracestate_snapshots(self):
        ts = TraceState([1, 2, 3])
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('one'), ModelStub(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('two'), ModelStub(b=2))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('three'), ModelStub(c=3))
        for act, exp in zip(ts, ['1', '2', '3']):
            self.assertEqual(act.id, exp)
        for act, exp in zip(ts, ['one', 'two', 'three']):
            self.assertEqual(act.scenario, exp)
        for act, exp in zip(ts, [dict(a=1), dict(b=2), dict(c=3)]):
            self.assertEqual(act.model, exp)

    def test_can_index_tracestate_snapshots(self):
        ts = TraceState([1, 2, 3])
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('one'), ModelStub(a=1))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('two'), ModelStub(b=2))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('three'), ModelStub(c=3))
        self.assertEqual(ts[0].id, '1')
        self.assertEqual(ts[1].scenario, 'two')
        self.assertEqual(ts[2].model, dict(c=3))
        self.assertEqual(ts[-1].scenario, 'three')
        self.assertEqual([s.id for s in ts[1:]], ['2', '3'])

    def test_adding_coverage_prevents_drought(self):
        ts = TraceState(range(3))
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('two'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(ts.next_candidate(), ScenarioStub('three'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)

    def test_repeated_scenarios_increases_drought(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 2)

    def test_drought_is_reset_with_new_coverage(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(2, ScenarioStub('two'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)

    def test_rewind_includes_drought_update(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub())
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(2, ScenarioStub('two'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.rewind()
        self.assertEqual(ts.coverage_drought, 1)
        ts.rewind()
        self.assertEqual(ts.coverage_drought, 0)


class TestPartialScenarios(unittest.TestCase):
    def test_push_partial_does_not_complete_coverage(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.coverage_reached(), False)

    def test_confirm_full_after_push_partial_completes_coverage(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(1, ScenarioStub('remainder'), ModelStub())
        self.assertEqual(ts.get_trace(), ['part1', 'part2', 'remainder'])
        self.assertIs(ts.coverage_reached(), True)

    def test_scenario_unavailble_once_pushed_partial(self):
        ts = TraceState([1])
        candidate = ts.next_candidate()
        ts.push_partial_scenario(candidate, ScenarioStub('part1'), ModelStub())
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_of_single_part(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_all_parts(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
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
        ts = TraceState([1])
        self.assertEqual(ts.next_candidate(), 1)
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_to_partial_scenario(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub(a=1))
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub(b=2))
        snapshot = ts.rewind()
        self.assertEqual(snapshot.id, '1.1')
        self.assertEqual(snapshot.scenario, 'part1')
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_last_part(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('one'), ModelStub(a=1))
        ts.push_partial_scenario(2, ScenarioStub('part1'), ModelStub(b=2))
        snapshot = ts.rewind()
        self.assertEqual(ts.get_trace(), ['one'])
        self.assertEqual(snapshot.id, '1')
        self.assertEqual(snapshot.scenario, 'one')
        self.assertEqual(snapshot.model, dict(a=1))

    def test_rewind_all_parts_of_completed_scenario_at_once(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub(a=1))
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub(b=2))
        ts.confirm_full_scenario(1, ScenarioStub('remainder'), ModelStub())
        tail = ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(tail, None)

    def test_tried_entries_after_rewind(self):
        ts = TraceState([1, 2, 10, 11, 12, 20, 21])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.reject_scenario(10)
        ts.reject_scenario(11)
        ts.confirm_full_scenario(2, ScenarioStub('two'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        ts.reject_scenario(20)
        ts.reject_scenario(21)
        self.assertEqual(ts.tried, (20, 21))
        ts.rewind()
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (10, 11, 2))
        ts.reject_scenario(12)
        self.assertEqual(ts.tried, (10, 11, 2, 12))
        ts.rewind()
        self.assertEqual(ts.tried, (1,))

    def test_highest_part_after_first_part(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertEqual(ts[-1].id, '1.1')
        self.assertEqual(ts.highest_part(1), 1)

    def test_highest_part_after_multiple_parts(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        self.assertEqual(ts[-1].id, '1.2')
        self.assertEqual(ts.highest_part(1), 2)

    def test_highest_part_after_completing_multiple_parts(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        ts.confirm_full_scenario(1, ScenarioStub('remainder'), ModelStub())
        self.assertEqual(ts[-1].id, '1.0')
        self.assertEqual(ts.highest_part(1), 0)

    def test_highest_part_after_partial_rewind(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        self.assertEqual(ts.highest_part(1), 2)
        ts.rewind()
        self.assertEqual(ts.highest_part(1), 1)
        ts.rewind()
        self.assertEqual(ts.highest_part(1), 0)

    def test_highest_part_is_0_when_no_refinement_is_ongoing(self):
        ts = TraceState([1])
        self.assertEqual(ts.highest_part(1), 0)
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub())
        ts.confirm_full_scenario(1, ScenarioStub('remainder'), ModelStub())
        self.assertEqual(ts.highest_part(1), 0)
        ts.rewind()
        self.assertEqual(ts.highest_part(1), 0)

    def test_count_scenario_repetitions_with_partials(self):
        ts = TraceState(range(2))
        first = ts.next_candidate()
        self.assertEqual(ts.count(first), 0)
        ts.confirm_full_scenario(first, ScenarioStub('full'), ModelStub())
        self.assertEqual(ts.count(first), 1)
        ts.push_partial_scenario(first, ScenarioStub('part1'), ModelStub())
        ts.push_partial_scenario(first, ScenarioStub('part2'), ModelStub())
        self.assertEqual(ts.count(first), 1)
        ts.confirm_full_scenario(first, ScenarioStub('remainder'), ModelStub())
        self.assertEqual(ts.count(first), 2)
        second = ts.next_candidate()
        ts.push_partial_scenario(second, ScenarioStub('part1'), ModelStub())
        self.assertEqual(ts.count(second), 0)
        ts.push_partial_scenario(second, ScenarioStub('part2'), ModelStub())
        ts.confirm_full_scenario(second, ScenarioStub('remainder'), ModelStub())
        self.assertEqual(ts.count(second), 1)

    def test_partial_scenario_is_tried_without_finishing(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub())
        self.assertEqual(ts.tried, ())
        ts.rewind()
        self.assertEqual(ts.tried, (1,))

    def test_get_last_snapshot_by_index(self):
        ts = TraceState([1])
        ts.push_partial_scenario(1, ScenarioStub('part1'), ModelStub(a=1))
        self.assertEqual(ts[-1].id, '1.1')
        self.assertEqual(ts[-1].scenario, 'part1')
        self.assertEqual(ts[-1].model, dict(a=1))
        self.assertEqual(ts[-1].coverage_drought, 0)
        ts.push_partial_scenario(1, ScenarioStub('part2'), ModelStub(b=2))
        ts.confirm_full_scenario(1, ScenarioStub('remainder'), ModelStub(c=3))
        self.assertEqual(ts[-1].id, '1.0')
        self.assertEqual(ts[-1].scenario, 'remainder')
        self.assertEqual(ts[-1].model, dict(c=3))
        self.assertEqual(ts[-1].coverage_drought, 0)

    def test_only_completed_scenarios_affect_drought(self):
        ts = TraceState([1, 2])
        ts.confirm_full_scenario(1, ScenarioStub('one full'), ModelStub())
        ts.push_partial_scenario(1, ScenarioStub('one part1'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)
        ts.confirm_full_scenario(1, ScenarioStub('one remainder'), ModelStub())
        self.assertEqual(ts.coverage_drought, 1)
        ts.push_partial_scenario(2, ScenarioStub('two part1'), ModelStub())
        self.assertEqual(ts.coverage_drought, 1)
        ts.confirm_full_scenario(2, ScenarioStub('two remainder'), ModelStub())
        self.assertEqual(ts.coverage_drought, 0)


class ScenarioStub(str):
    """Stub for suitedata.Scenario"""


class ModelStub(dict):
    """Stub for modelspace.ModelSpace"""


if __name__ == '__main__':
    unittest.main()
