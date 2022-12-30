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
        self.assertIs(ts.can_rewind(), 0)

    def test_completing_single_size_trace(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        self.assertIs(ts.coverage_reached(), False)
        ts.confirm_full_scenario(0, 0, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [0])

    def test_trying_excludes_scenario_from_candidacy(self):
        ts = TraceState(1)
        self.assertEqual(ts.next_candidate(), 0)
        ts.reject_scenario(0)
        self.assertIs(ts.next_candidate(), None)

    def test_rewind_returns_the_rewinded_snapshot(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 'foo', {})
        rewinded = ts.rewind()
        self.assertEqual(rewinded.scenario, 'foo')

    def test_rewind_single_available_scenario(self):
        ts = TraceState(1)
        ts.confirm_full_scenario(0, 0, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertIs(ts.can_rewind(), 1)
        ts.rewind()
        self.assertIs(ts.can_rewind(), 0)
        self.assertIs(ts.coverage_reached(), False)
        self.assertEqual(ts.next_candidate(), None)
        self.assertEqual(ts.get_trace(), [])

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
        ts.confirm_full_scenario(second, second, {})
        self.assertIs(ts.coverage_reached(), True)
        self.assertEqual(ts.get_trace(), [first, third, second])
        self.assertEqual(rejected, second)

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
        self.assertEqual(ts.get_trace(), [retry_first, retry_second, retry_third])
