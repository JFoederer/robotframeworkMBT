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


class TestPartialScenarios(unittest.TestCase):
    def test_push_partial_does_not_complete_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'remainder')
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.coverage_reached(), False)

    def test_confirm_full_after_push_partial_completes_coverage(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2+remainder')
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, 'part2', {}, 'remainder')
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts.get_trace(), ['part1', 'part2', 'remainder'])
        self.assertIs(ts.coverage_reached(), True)

    def test_scenario_unavailble_once_pushed_partial(self):
        ts = TraceState(1)
        candidate = ts.next_candidate()
        ts.push_partial_scenario(candidate, 'part1', {}, 'remainder')
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_of_single_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'remainder')
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.can_rewind(), True)
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])

    def test_rewind_all_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2+remainder')
        self.assertIs(ts.coverage_reached(), False)
        ts.push_partial_scenario(0, 'part2', {}, 'remainder')
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
        ts.push_partial_scenario(0, 'part1', {}, 'remainder')
        ts.rewind()
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_to_partial_scenario(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', dict(a=1), 'part2+remainder')
        ts.push_partial_scenario(0, 'part2', dict(b=2), 'remainder')
        snapshot = ts.rewind()
        self.assertEqual(snapshot.id, '0.1')
        self.assertEqual(snapshot.scenario, 'part1')
        self.assertEqual(snapshot.model, dict(a=1))
        self.assertEqual(snapshot.remainder, 'part2+remainder')

    def test_rewind_last_part(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'one', dict(a=1))
        ts.push_partial_scenario(1, 'part1', dict(b=2), 'remainder')
        snapshot = ts.rewind()
        self.assertEqual(ts.get_trace(), ['one'])
        self.assertEqual(snapshot.id, '0')
        self.assertEqual(snapshot.scenario, 'one')
        self.assertEqual(snapshot.model, dict(a=1))
        self.assertIs(snapshot.remainder, None)

    def test_rewind_all_parts_of_completed_scenario_at_once(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', dict(a=1), 'part2+remainder')
        ts.push_partial_scenario(0, 'part2', dict(b=2), 'remainder')
        ts.confirm_full_scenario(0, 'remainder', {})
        tail = ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(tail, None)


class TestRefinement(unittest.TestCase):
    def test_single_step_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'one: part1', {}, 'one: remainder')
        candidate2 = ts.next_candidate()
        self.assertNotEqual(candidate1, candidate2)
        ts.confirm_full_scenario(candidate2, 'two', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(candidate1, 'one: remainder', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one: part1', 'two', 'one: remainder'])

    def test_rewind_step_with_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'part1', {}, 'remainder')
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, 'two', {})
        ts.confirm_full_scenario(candidate1, 'remainder', {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), [])
        self.assertIs(ts.next_candidate(), candidate2)
        self.assertIs(ts.coverage_reached(), False)

    def test_rewind_refinement(self):
        ts = TraceState(2)
        candidate1 = ts.next_candidate()
        ts.push_partial_scenario(candidate1, 'part1', {}, 'remainder')
        candidate2 = ts.next_candidate()
        ts.confirm_full_scenario(candidate2, 'two', {})
        ts.rewind()
        self.assertEqual(ts.get_trace(), ['part1'])
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), False)

    def test_refinement_at_two_steps(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'one 1.1', {}, '1.2+1.0')
        ts.confirm_full_scenario(ts.next_candidate(), 'two', {})
        ts.push_partial_scenario(outer, 'one 1.2', {}, 'remainder (1.0)')
        ts.confirm_full_scenario(ts.next_candidate(), 'three', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, 'one 1.0', {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one 1.1', 'two', 'one 1.2', 'three', 'one 1.0'])

    def test_rewind_to_swap_refinements(self):
        ts = TraceState(3)
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'one 1.1', {}, '1.2+1.0')
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, 'inner one', {})
        ts.push_partial_scenario(outer, 'one 1.2', {}, 'remainder (1.0)')
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        self.assertEqual(ts.next_candidate(), inner2)
        ts.confirm_full_scenario(inner2, 'inner 2', {})
        ts.push_partial_scenario(outer, 'one 1.2', {}, 'remainder (1.0)')
        self.assertEqual(ts.next_candidate(), inner1)
        ts.confirm_full_scenario(ts.next_candidate(), 'inner 1', {})
        self.assertIs(ts.coverage_reached(), False)
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(outer, 'one 1.0', {})
        self.assertIs(ts.next_candidate(), None)
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['one 1.1', 'inner 2', 'one 1.2', 'inner 1', 'one 1.0'])

    def test_rewind_partial_scenario_to_before_outer(self):
        ts = TraceState(4)
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, 'head', {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'one 1.1', {}, '1.2+1.0')
        inner1 = ts.next_candidate()
        ts.confirm_full_scenario(inner1, 'inner one', {})
        ts.push_partial_scenario(outer, 'one 1.2', {}, 'remainder (1.0)')
        inner2 = ts.next_candidate()
        ts.reject_scenario(inner2)
        ts.rewind()
        ts.rewind()
        previous = ts.rewind()
        self.assertEqual(previous.scenario, 'head')
        self.assertEqual(ts.get_trace(), ['head'])
        self.assertNotIn(ts.next_candidate(), [head, outer])

    def test_rewind_scenario_with_double_refinement_as_one(self):
        ts = TraceState(4)
        head = ts.next_candidate()
        ts.confirm_full_scenario(head, 'head', {})
        outer = ts.next_candidate()
        ts.push_partial_scenario(outer, 'one 1.1', {}, '1.2+1.0')
        ts.confirm_full_scenario(ts.next_candidate(), 'inner one', {})
        ts.push_partial_scenario(outer, 'one 1.2', {}, 'remainder (1.0)')
        ts.confirm_full_scenario(ts.next_candidate(), 'inner two', {})
        ts.confirm_full_scenario(outer, 'one 1.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertEqual(previous.scenario, 'head')
        self.assertEqual(ts.get_trace(), ['head'])
        self.assertIs(ts.coverage_reached(), False)
        self.assertNotEqual(ts.next_candidate(), [head, outer])

    def test_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T.1', {}, 'T.0')
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M.1', {},'M.0')
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, 'L', {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, 'M.0', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, 'T.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T.1', 'M.1', 'L', 'M.0', 'T.0'])

    def test_rewind_to_swap_nested_refinement(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T.1', {}, 'T.0')
        lower_level = ts.next_candidate()
        ts.push_partial_scenario(lower_level, 'L.1', {},'L.0')
        middle_level = ts.next_candidate()
        ts.reject_scenario(middle_level)
        self.assertIs(ts.next_candidate(), None)
        ts.rewind()
        self.assertEqual(ts.next_candidate(), middle_level)
        ts.push_partial_scenario(middle_level, 'M.1', {},'M.0')
        ts.confirm_full_scenario(lower_level, 'L', {})
        self.assertIs(ts.next_candidate(), None)
        ts.confirm_full_scenario(middle_level, 'M.0', {})
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(top_level, 'T.0', {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), ['T.1', 'M.1', 'L', 'M.0', 'T.0'])

    def test_rewind_nested_refinement_as_one(self):
        ts = TraceState(4)
        ts.confirm_full_scenario(ts.next_candidate(), 'head', {})
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T.1', {}, 'T.0')
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M.1', {},'M.0')
        lower_level = ts.next_candidate()
        ts.confirm_full_scenario(lower_level, 'L', {})
        ts.confirm_full_scenario(middle_level, 'M.0', {})
        self.assertIs(ts.next_candidate(), None)
        previous = ts.rewind()
        self.assertIs(ts.next_candidate(), lower_level)
        self.assertIs(previous.scenario, 'T.1')
        self.assertEqual(ts.get_trace(), ['head', 'T.1'])

    def test_rewind_scenario_with_nested_refinement_as_one(self):
        ts = TraceState(3)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T.1', {}, 'T.0')
        middle_level = ts.next_candidate()
        ts.push_partial_scenario(middle_level, 'M.1', {},'M.0')
        ts.confirm_full_scenario(ts.next_candidate(), 'L', {})
        ts.confirm_full_scenario(middle_level, 'M.0', {})
        ts.confirm_full_scenario(top_level, 'T.0', {})
        self.assertIs(ts.coverage_reached(), True)
        previous = ts.rewind()
        self.assertIs(previous, None)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.get_trace(), [])

    def test_highest_part_when_index_not_present(self):
        ts = TraceState(1)
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_for_non_partial_sceanrio(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'one', {})
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_after_first_part(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part', {}, 'remainder')
        self.assertEqual(ts.highest_part(0), 1)

    def test_highest_part_after_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2..3+remainder')
        ts.push_partial_scenario(0, 'part2', {}, 'part3+remainder')
        ts.push_partial_scenario(0, 'part3', {}, 'remainder')
        self.assertEqual(ts.highest_part(0), 3)

    def test_highest_part_after_completing_multiple_parts(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2..3+remainder')
        ts.push_partial_scenario(0, 'part2', {}, 'part3+remainder')
        ts.push_partial_scenario(0, 'part3', {}, 'remainder')
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts.highest_part(0), 3)

    def test_highest_part_after_partial_rewind(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2..3+remainder')
        ts.push_partial_scenario(0, 'part2', {}, 'part3+remainder')
        ts.push_partial_scenario(0, 'part3', {}, 'remainder')
        self.assertEqual(ts.highest_part(0), 3)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 2)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 1)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_part_after_full_rewind(self):
        ts = TraceState(1)
        ts.push_partial_scenario(0, 'part1', {}, 'part2..3+remainder')
        ts.push_partial_scenario(0, 'part2', {}, 'part3+remainder')
        ts.push_partial_scenario(0, 'part3', {}, 'remainder')
        ts.confirm_full_scenario(0, 'remainder', {})
        self.assertEqual(ts.highest_part(0), 3)
        ts.rewind()
        self.assertEqual(ts.highest_part(0), 0)

    def test_highest_parts_from_refined_scenario(self):
        ts = TraceState(4)
        top_level = ts.next_candidate()
        ts.push_partial_scenario(top_level, 'T.1', {}, 'T.2, T.0')
        middle_level_1 = ts.next_candidate()
        ts.push_partial_scenario(middle_level_1, 'M1.1', {},'M1.0')
        lower_level = ts.next_candidate()
        ts.push_partial_scenario(lower_level, 'L.1', {}, 'L.2,3,0')
        ts.push_partial_scenario(lower_level, 'L.2', {}, 'L.3,0')
        ts.push_partial_scenario(lower_level, 'L.3', {}, 'L.0')
        ts.confirm_full_scenario(lower_level, 'L.0', {})
        ts.confirm_full_scenario(middle_level_1, 'M1.0', {})
        ts.push_partial_scenario(top_level, 'T.2', {}, 'T.0')
        ts.confirm_full_scenario(ts.next_candidate(), 'M2', {})
        ts.confirm_full_scenario(top_level, 'T.0', {})
        self.assertEqual(ts.highest_part(top_level), 2)
        self.assertEqual(ts.highest_part(middle_level_1), 1)
        self.assertEqual(ts.highest_part(lower_level), 3)
