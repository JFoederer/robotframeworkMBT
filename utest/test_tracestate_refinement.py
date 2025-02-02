# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2025, J. Foederer
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


class TestTraceStateRefinement(unittest.TestCase):
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

    def test_initially_no_scenario_is_in_refinement(self):
        ts = TraceState(1)
        self.assertEqual(ts.find_scenarios_with_active_refinement(), [])

    def test_full_scenario_is_not_reported_as_refinement(self):
        ts = TraceState(2)
        ts.confirm_full_scenario(0, 'S1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), [])

    def test_push_partial_opens_refinement(self):
        ts = TraceState(4)
        ts.push_partial_scenario(0, 'S1.1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['S1.1'])

    def test_nested_refinements_are_all_reported_as_in_refinement(self):
        ts = TraceState(4)
        ts.push_partial_scenario(0, 'T1.1', {})
        ts.push_partial_scenario(1, 'M1.1', {})
        ts.push_partial_scenario(2, 'B1.1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1', 'B1.1'])

    def test_closing_refinement_removes_it_from_list(self):
        ts = TraceState(4)
        ts.push_partial_scenario(0, 'T1.1', {})
        ts.push_partial_scenario(1, 'M1.1', {})
        ts.push_partial_scenario(2, 'B1.1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1', 'B1.1'])
        ts.confirm_full_scenario(2, 'B1.0', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1'])

    def test_multi_step_refinement_is_reported_only_once(self):
        ts = TraceState(4)
        ts.push_partial_scenario(0, 'T1.1', {})
        ts.push_partial_scenario(1, 'M1.1', {})
        ts.confirm_full_scenario(2, 'B1', {})
        ts.push_partial_scenario(1, 'M1.2', {})
        ts.confirm_full_scenario(3, 'B2', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1'])

    def test_rewind_open_refinement_removes_it_from_list(self):
        ts = TraceState(4)
        ts.push_partial_scenario(0, 'T1.1', {})
        ts.push_partial_scenario(1, 'M1.1', {})
        ts.push_partial_scenario(2, 'B1.1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1', 'B1.1'])
        ts.rewind()
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T1.1', 'M1.1'])

    def test_rewind_finished_scenario_with_refinement_removes_enclosed_refinements(self):
        ts = TraceState(5)
        ts.confirm_full_scenario(0, 'T1', {})
        ts.push_partial_scenario(1, 'T2.1', {})
        ts.push_partial_scenario(2, 'M1.1', {})
        ts.push_partial_scenario(3, 'B1.1', {})
        ts.confirm_full_scenario(4, 'S1', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T2.1', 'M1.1', 'B1.1'])
        ts.confirm_full_scenario(3, 'B1.0', {})
        ts.confirm_full_scenario(2, 'M1.0', {})
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T2.1'])
        ts.rewind() # Middle including its Bottom refinement
        self.assertEqual(ts.find_scenarios_with_active_refinement(), ['T2.1'])


if __name__ == '__main__':
    unittest.main()
