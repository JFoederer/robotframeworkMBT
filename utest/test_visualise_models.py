# BSD 3-Clause License
#
# Copyright (c) 2026, T.B. Dubbeling,  J. Foederer, T.S. Kas, D.R. Osinga, D.F. Serra e Silva, J.C. Willegers
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

try:
    from robotmbt.visualise.models import *

    VISUALISE = True
except ImportError:
    VISUALISE = False

if VISUALISE:
    class TestVisualiseModels(unittest.TestCase):
        """
        Contains tests for robotmbt/visualise/models.py
        """

        """
        Class: ScenarioInfo
        """

        def test_scenarioInfo_str(self):
            si = ScenarioInfo('test')
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 'test')

        def test_scenarioInfo_Scenario(self):
            s = Scenario('test')
            s.src_id = 0
            si = ScenarioInfo(s)
            self.assertEqual(si.name, 'test')
            self.assertEqual(si.src_id, 0)

        def test_split_name_empty_string(self):
            result = ScenarioInfo._split_name("")
            self.assertEqual(result, "")
            self.assertNotIn('\n', result)

        def test_split_name_single_short_word(self):
            result = ScenarioInfo._split_name("Hello")
            self.assertEqual(result, "Hello")
            self.assertNotIn('\n', result)

        def test_split_name_single_exact_length_word(self):
            exact_20 = "abcdefghijklmnopqrst"
            result = ScenarioInfo._split_name(exact_20)
            self.assertEqual(result, exact_20)
            self.assertNotIn('\n', result)

        def test_split_name_single_long_word(self):
            name = "ThisIsAReallyLongNameWithoutAnySpacesAtAll"
            result = ScenarioInfo._split_name(name)
            self.assertEqual(result, name)
            self.assertNotIn('\n', result)

        def test_split_name_two_words_short(self):
            result = ScenarioInfo._split_name("Hello World")
            self.assertEqual(result, "Hello World")
            self.assertNotIn('\n', result)

        def test_split_name_two_words_exceeds_limit(self):
            name = "Supercalifragilistic Hello"
            result = ScenarioInfo._split_name(name)

            self.assertEqual(result.replace('\n', ' '), name)
            self.assertIn('\n', result)

        def test_split_name_multiple_words_need_split(self):
            name = "This is a very long scenario name that should be split"
            result = ScenarioInfo._split_name(name)

            self.assertEqual(result.replace('\n', ' '), name)
            self.assertIn('\n', result)

        """
        Class: StateInfo
        """

        def test_stateInfo_empty(self):
            s = StateInfo(ModelSpace())
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_empty(self):
            space = ModelSpace()
            space.props['prop1'] = ModelSpace()
            s = StateInfo(space)
            self.assertEqual(str(s), '')

        def test_stateInfo_prop_val(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            space.props['prop1'] = prop1
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))

        def test_stateInfo_prop_val_empty(self):
            space = ModelSpace()
            prop1 = ModelSpace()
            prop1.value = 1
            prop2 = ModelSpace()
            space.props['prop1'] = prop1
            space.props['prop2'] = prop2
            s = StateInfo(space)
            self.assertTrue('prop1:' in str(s))
            self.assertTrue('value=1' in str(s))
            self.assertFalse('prop2:' in str(s))

        """
        Class: TraceInfo
        """

        def test_trace_info_update_normal(self):
            info = TraceInfo()

            self.assertEqual(len(info.current_trace), 0)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 3)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 0)

        def test_trace_info_update_backtrack(self):
            info = TraceInfo()

            self.assertEqual(len(info.current_trace), 0)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 3)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 0)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 2)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 1)]), 1)

            self.assertEqual(len(info.current_trace), 1)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 4)]), 2)

            self.assertEqual(len(info.current_trace), 2)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 5)]), 3)

            self.assertEqual(len(info.current_trace), 3)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

            info.update_trace(ScenarioInfo('test'), StateInfo._create_state_with_prop('prop', [('value', 6)]), 4)

            self.assertEqual(len(info.current_trace), 4)
            self.assertEqual(len(info.all_traces), 1)
            self.assertEqual(len(info.all_traces[0]), 3)

if __name__ == '__main__':
    unittest.main()
