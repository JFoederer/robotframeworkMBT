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
from unittest.mock import patch

from robotmbt.suiteprocessors import SuiteProcessors


@patch('robotmbt.suiteprocessors.random.seed')
class TestRandomSeeding(unittest.TestCase):
    def test_provided_seed_is_used_as_is(self, mock):
        SuiteProcessors._init_randomiser("specific seed")
        mock.assert_called_with("specific seed")

    def test_provided_seed_is_stripped(self, mock):
        SuiteProcessors._init_randomiser(" specific seed\t")
        mock.assert_called_with("specific seed")

    def test_seed_none_keeps_system_seed(self, mock):
        SuiteProcessors._init_randomiser(None)
        mock.assert_not_called()

    def test_seed_none_as_string(self, mock):
        SuiteProcessors._init_randomiser("None")
        mock.assert_not_called()

    def test_seed_none_as_string_is_stripped(self, mock):
        SuiteProcessors._init_randomiser(" None\t")
        mock.assert_not_called()

    def test_seed_none_as_string_is_case_insensitive(self, mock):
        SuiteProcessors._init_randomiser("nOnE")
        mock.assert_not_called()

    def test_seed_new_generates_reusable_seed(self, mock):
        SuiteProcessors._init_randomiser("new")
        self._is_generated_seed(mock.call_args.args[0])

    def test_seed_new_is_stripped(self, mock):
        SuiteProcessors._init_randomiser(" new\t")
        self._is_generated_seed(mock.call_args.args[0])

    def test_seed_new_is_case_insensitive(self, mock):
        SuiteProcessors._init_randomiser("NeW")
        self._is_generated_seed(mock.call_args.args[0])

    def test_generated_seeds_have_max_2_consecutive_vowels_or_consonants(self, mock):
        for _ in range(20):
            SuiteProcessors._init_randomiser("new")
            new_seed = mock.call_args.args[0]
            self._is_generated_seed(new_seed)
            self.assertNotIn('***', new_seed.translate({ord(c):'*' for c in 'aeiouy'}))
            self.assertNotIn('***', new_seed.translate({ord(c):'*' for c in 'bcdfghjklmnpqrstvwxz'}))

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


if __name__ == '__main__':
    unittest.main()
