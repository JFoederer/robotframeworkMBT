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
from unittest.mock import patch, call

from robotmbt.suiteprocessors import ModelBased
from robotmbt.suitedata import Suite, Scenario, Step


@patch('robotmbt.suiteprocessors.random.seed')
class TestRandomSeeding(unittest.TestCase):
    def test_provided_seed_is_used_as_is(self, mock):
        ModelBased._init_randomiser("specific seed")
        mock.assert_called_with("specific seed")

    def test_provided_seed_is_stripped(self, mock):
        ModelBased._init_randomiser(" specific seed\t")
        mock.assert_called_with("specific seed")

    def test_seed_none_keeps_system_seed(self, mock):
        ModelBased._init_randomiser(None)
        mock.assert_called_with()

    def test_seed_none_as_string(self, mock):
        ModelBased._init_randomiser("None")
        mock.assert_called_with()

    def test_seed_none_as_string_is_stripped(self, mock):
        ModelBased._init_randomiser(" None\t")
        mock.assert_called_with()

    def test_seed_none_as_string_is_case_insensitive(self, mock):
        ModelBased._init_randomiser("nOnE")
        mock.assert_called_with()

    def test_seed_new_generates_reusable_seed(self, mock):
        ModelBased._init_randomiser("new")
        self._is_generated_seed(mock.call_args.args[0])

    def test_seed_new_is_stripped(self, mock):
        ModelBased._init_randomiser(" new\t")
        self._is_generated_seed(mock.call_args.args[0])

    def test_seed_new_is_case_insensitive(self, mock):
        ModelBased._init_randomiser("NeW")
        self._is_generated_seed(mock.call_args.args[0])

    def test_generated_seeds_have_max_2_consecutive_vowels_or_consonants(self, mock):
        for _ in range(20):
            ModelBased._init_randomiser("new")
            new_seed = mock.call_args.args[0]
            self._is_generated_seed(new_seed)
            self.assertNotIn('***', new_seed.translate({ord(c): '*' for c in 'aeiouy'}))
            self.assertNotIn('***', new_seed.translate({ord(c): '*' for c in 'bcdfghjklmnpqrstvwxz'}))

    def test_seed_is_reset_after_using_specific_seed(self, mock):
        """
        added to cover the issue where, after having rerun a specific trace, the next
        generated seed was always the same.
        """
        ModelBased._init_randomiser("specific seed")
        ModelBased._init_randomiser("new")
        new_seed = mock.call_args.args[0]
        mock.assert_has_calls([call("specific seed"), call(), call(new_seed)])

    def _is_generated_seed(self, arg):
        """
        Generated seeds are formatted as 5 dash-separated [-] words, where
        each word is 3 up to and including 6 letters [a-z] long.
        """
        words = arg.split("-")
        self.assertEqual(len(words), 5)
        for word in words:
            self.assertTrue(word.isalpha())
            self.assertTrue(3 <= len(word) <= 6)


class TestBatchSize(unittest.TestCase):
    def setUp(self):
        self.suite = Suite('testsuite')
        init_scenario = Scenario('init scenario', self.suite, RobotTestCaseStub())
        init_step = Step('init keyword', parent=init_scenario)
        init_step.model_info = dict(IN=["new prop"], OUT=["prop.flag = True"])
        init_scenario.steps = [init_step]
        body_scenario = Scenario('body scenario', self.suite, RobotTestCaseStub())
        self.scenario_name_without_rep_count = len('body scenario')
        step = Step('action keyword', parent=body_scenario)
        step.model_info = dict(IN=["prop.flag = not prop.flag"], OUT=[])  # force a change so retries are not rejected
        body_scenario.steps = [step]
        self.suite.scenarios = [init_scenario, body_scenario]
        self.processor = ModelBased()

    def test_batch_size_1(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=3, batch_size=1)
        self.assertEqual(self.processor.scenarios_pending, 1)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 1)
        self.assertEqual(self.processor.scenarios_committed, 1)
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 2)
        self.assertEqual(self.processor.scenarios_committed, 2)
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 3)
        self.assertEqual(self.processor.scenarios_committed, 3)
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.assertListEqual([s.name[:self.scenario_name_without_rep_count] for s in out_suite.scenarios],
                             ['init scenario'] + ['body scenario']*(out_suite.scenario_count()-1))

    def test_batch_size_2_last_batch_not_full(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=3, batch_size=2)
        self.assertEqual(self.processor.scenarios_pending, 2)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 1)
        self.assertEqual(self.processor.scenarios_committed, 1)
        self.assertEqual(self.processor.scenarios_pending, 1)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.assertEqual(out_suite.scenario_count(), 3)

    def test_batch_size_2_last_batch_full(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=4, batch_size=2)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 1)
        self.assertEqual(self.processor.scenarios_committed, 1)
        self.assertEqual(self.processor.scenarios_pending, 1)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 1)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.assertEqual(out_suite.scenario_count(), 4)

    def test_batch_size_10(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=15, batch_size=10)
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 1)
        self.assertEqual(self.processor.scenarios_pending, 9)
        for _ in range(9):
            self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 10)
        self.assertEqual(self.processor.scenarios_pending, 0)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 4)

    def test_batch_size_3_is_trace_length(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=3, batch_size=3)
        self.assertEqual(self.processor.scenarios_pending, 3)
        self.processor.next_scenario_request()
        self.assertEqual(self.processor.scenarios_pending, 2)
        self.processor.next_scenario_request()
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 3)
        self.assertListEqual([s.name[:self.scenario_name_without_rep_count] for s in out_suite.scenarios],
                             ['init scenario'] + ['body scenario']*(out_suite.scenario_count()-1))

    def test_requesting_beyond_targets_has_no_effect(self):
        out_suite = self.processor.process_test_suite(self.suite, scenario_target=3, batch_size=3)
        self.processor.next_scenario_request()
        self.processor.next_scenario_request()
        self.assertFalse(self.processor.are_all_targets_reached())
        self.processor.next_scenario_request()
        self.assertEqual(out_suite.scenario_count(), 3)
        self.assertTrue(self.processor.are_all_targets_reached())
        self.processor.next_scenario_request()
        self.assertTrue(self.processor.are_all_targets_reached())
        self.assertEqual(out_suite.scenario_count(), 3)

    def test_multi_batch(self):
        """Check some variations in batch size versus target size"""
        for target, batch in [(1, 1),     # Smallest target and batch
                              (23, 3),    # Multiple batches needed te completer
                              (10, 24),   # Batch size exceeds target size
                              (15, 14),   # Batch size just not enough
                              (16, 16)    # Batch size equals target size
                              ]:
            out_suite = self.processor.process_test_suite(self.suite, coverage_target=0,
                                                          scenario_target=target, batch_size=batch)
            while not self.processor.are_all_targets_reached():
                self.processor.next_scenario_request()
            self.assertEqual(out_suite.scenario_count(), target)
            self.assertListEqual([s.name[:self.scenario_name_without_rep_count] for s in out_suite.scenarios],
                                 ['init scenario'] + ['body scenario']*(out_suite.scenario_count()-1))


class RobotTestCaseStub:
    def copy(self, **kwargs):
        pass


if __name__ == '__main__':
    unittest.main()
