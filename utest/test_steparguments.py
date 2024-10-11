# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2024, J. Foederer
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

from robotmbt.steparguments import StepArgument, StepArguments


class TestStepArgument(unittest.TestCase):
    def test_arg_is_in_robot_notation(self):
        arg1 = StepArgument('foo', 7)
        arg2 = StepArgument('foo bar', 7)
        arg3 = StepArgument('foo_bar', 7)
        self.assertEqual(arg1.arg, '${foo}')
        self.assertEqual(arg2.arg, '${foo bar}')
        self.assertEqual(arg3.arg, '${foo_bar}')

    def test_value_is_kept_as_is_number(self):
        arg1 = StepArgument('foo', 7)
        arg2 = StepArgument('foo', 2.7)
        arg3 = StepArgument('foo', -8)
        self.assertEqual(arg1.value, 7)
        self.assertEqual(arg2.value, 2.7)
        self.assertEqual(arg3.value, -8)

    def test_value_is_kept_as_is_str(self):
        arg1 = StepArgument('foo', 'bar')
        arg2 = StepArgument('foo', 'bar bar ')
        arg3 = StepArgument('foo', '${bar}')
        arg4 = StepArgument('foo', '\t')
        self.assertEqual(arg1.value, 'bar')
        self.assertEqual(arg2.value, 'bar bar ')
        self.assertEqual(arg3.value, '${bar}')
        self.assertEqual(arg4.value, '\t')

    def test_value_is_kept_as_is_immutable(self):
        arg1 = StepArgument('foo', None)
        arg2 = StepArgument('foo', True)
        arg3 = StepArgument('foo', False)
        self.assertEqual(arg1.value, None)
        self.assertEqual(arg2.value, True)
        self.assertEqual(arg3.value, False)

    def test_original_value_is_kept_when_changing_value(self):
        """helps to restore the original step text"""
        arg1 = StepArgument('foo', 7)
        self.assertEqual(arg1.value, 7)
        arg1.value = 8
        self.assertEqual(arg1.org_value, 7)
        self.assertEqual(arg1.value, 8)

    def test_copies_are_the_same(self):
        arg1 = StepArgument('foo', 7)
        arg2 = arg1.copy()
        self.assertEqual(arg1.arg, arg2.arg)
        self.assertEqual(arg1.value, arg2.value)
        self.assertEqual(arg1.org_value, arg2.org_value)
        self.assertEqual(arg1.codestring, arg2.codestring)

    def test_original_value_is_kept_when_copying(self):
        arg1 = StepArgument('foo', 7)
        arg1.value = 8
        arg2 = arg1.copy()
        self.assertEqual(arg2.org_value, 7)
        self.assertEqual(arg2.value, 8)

    def test_copies_are_independent(self):
        arg1 = StepArgument('foo', 7)
        arg1.value = 8
        arg2 = arg1.copy()
        arg2.value = 13
        self.assertEqual(arg2.value, 13)
        self.assertEqual(arg1.value, 8)
        self.assertEqual(arg1.org_value, arg2.org_value)

    def test_bool_and_none_values_are_kept_for_code(self):
        arg1 = StepArgument('foo', None)
        arg2 = StepArgument('foo', True)
        arg3 = StepArgument('foo', False)
        self.assertEqual(arg1.codestring, 'None')
        self.assertEqual(arg2.codestring, 'True')
        self.assertEqual(arg3.codestring, 'False')

    def test_number_values_stay_numbers_for_code(self):
        arg1 = StepArgument('foo', 1)
        arg2 = StepArgument('foo', 0)
        arg3 = StepArgument('foo', -1)
        arg4 = StepArgument('foo', 2.7)
        arg5 = StepArgument('foo', 12E-1)
        arg6 = StepArgument('foo', 0xa)
        self.assertEqual(arg1.codestring, '1')
        self.assertEqual(arg2.codestring, '0')
        self.assertEqual(arg3.codestring, '-1')
        self.assertEqual(arg4.codestring, '2.7')
        self.assertEqual(arg5.codestring, '1.2')
        self.assertEqual(arg6.codestring, '10')

    def test_empty_string_stays_empty(self):
        arg1 = StepArgument('foo', '')
        self.assertEqual(arg1.codestring, '')

    def test_spaces_and_underscores_are_interchangable(self):
        arg1 = StepArgument('foo', 'foo bar')
        arg2 = StepArgument('foo', 'foo_bar')
        self.assertEqual(arg1.codestring, arg2.codestring)

    def test_other_values_become_unique_identifiers(self):
        valuelist = ['bar', 'foo bar', 'foo2bar', '${bar}',  # strings
                     ' ', '\t', '\n', '  ', ' \n', '\a',     # whitespace/non-printable
                     '#', '+-', '-+', '"', "'", 'パイ',      # special characters
                     max, 'elif', 'import', 'new', 'del',    # reserved words
                     lambda x: x/2, self, unittest.TestCase] # functions and objects
        argsset = set()
        for v in valuelist:
            arg = StepArgument('foo', v)
            self.assertTrue(arg.codestring.isidentifier())
            argsset.add(arg.codestring)
        self.assertEqual(len(valuelist), len(argsset))

    def test_valid_identifiers_remain_unchanged(self):
        arg1 = StepArgument('foo', 'bar')
        arg2 = StepArgument('foo', 'bar1')
        arg3 = StepArgument('foo', 'foo_bar')
        arg4 = StepArgument('foo', '__bar')
        arg5 = StepArgument('foo', 'class_')
        arg6 = StepArgument('foo', 'パ')
        self.assertEqual(arg1.codestring, 'bar')
        self.assertEqual(arg2.codestring, 'bar1')
        self.assertEqual(arg3.codestring, 'foo_bar')
        self.assertEqual(arg4.codestring, '__bar')
        self.assertEqual(arg5.codestring, 'class_')
        self.assertEqual(arg6.codestring, 'パ')

    def test_identical_values_yield_same_codestring(self):
        arg1 = StepArgument('foo1', 'bar')
        arg2 = StepArgument('foo2', 'bar')
        self.assertEqual(arg1.codestring, arg2.codestring)
        arg3 = StepArgument('foo1', '1A')
        arg4 = StepArgument('foo2', '1A')
        self.assertEqual(arg3.codestring, arg4.codestring)
        arg5 = StepArgument('foo1', ' +')
        arg6 = StepArgument('foo2', ' +')
        self.assertEqual(arg5.codestring, arg6.codestring)

    def test_number_bool_none_identifiers(self):
        valuelist = [1, 0, -1, None, True, False]
        for v in valuelist:
            idf = StepArgument.make_identifier(v)
            self.assertTrue(idf.isidentifier())
            self.assertTrue(idf not in [str(elm) for elm in valuelist])

    def test_keep_identifier_names_close_to_original(self):
        self.assertEqual(StepArgument.make_identifier('foo bar'), 'foo_bar')
        self.assertTrue(StepArgument.make_identifier('import').startswith('import'))
        self.assertTrue(StepArgument.make_identifier('4foo2bar').endswith('foo2bar'))


class TestStepArguments(unittest.TestCase):
    def test_empty_string_stays_empty(self):
        argset1 = StepArguments()
        self.assertEqual(argset1.fill_in_args(""), "")
        argset2 = StepArguments([StepArgument('foo', 'bar')])
        self.assertEqual(argset2.fill_in_args(""), "")

    def test_replace_single_argument(self):
        argset = StepArguments([StepArgument('foo', 'bar')])
        self.assertEqual(argset.fill_in_args("${foo}"), "bar")

    def test_replace_multiple_arguments(self):
        argset = StepArguments([StepArgument('foo1', 'bar1'),
                                StepArgument('foo2', 'bar2')])
        self.assertEqual(argset.fill_in_args("${foo1} ${foo2}"), "bar1 bar2")
        self.assertEqual(argset.fill_in_args("${foo2} ${foo1}"), "bar2 bar1")

    def test_same_argument_can_be_replaced_more_than_once(self):
        argset = StepArguments([StepArgument('foo', 'bar')])
        self.assertEqual(argset.fill_in_args("${foo} ${foo}"), "bar bar")

    def test_arguments_can_be_replaced_in_any_string(self):
        argset = StepArguments([StepArgument('foo1', 'bar1'),
                                StepArgument('foo2', 'bar2')])
        self.assertEqual(argset.fill_in_args("\t${foo1} and ${foo2}@#$%s  $$$$${foo2}${foo1}}"),
                                             "\tbar1 and bar2@#$%s  $$$$bar2bar1}")

    def test_can_use_robot_arguments_in_code_fragments(self):
        args = StepArguments([StepArgument('foo1', '3bar'), # 3bar needs to be converted to a valid identifier
                              StepArgument('foo2', '3bar')])
        assignment = "${foo1} = 'magic'"
        exec(args.fill_in_args(assignment, as_code=True), locals())
        expr = "${foo2} == 'magic'"
        # both foo1 and foo1 should map to the same identfier, because they were passed the same value.
        # If it is not a valid identifier, the exec command fails,
        # otherwise it is assigned the fixed string value, ready for comparison
        self.assertTrue(eval(args.fill_in_args(expr, as_code=True), locals()))

    def test_new_argument_sets_are_independent_of_their_source(self):
        arg1 = StepArgument('foo1', 'bar1')
        arg2 = StepArgument('foo2', 'bar2')
        arg2.value = 'extra bar'
        firstset = StepArguments([arg1, arg2])
        secondset = StepArguments(firstset)
        for arg in secondset:
            arg.value = 'new value'
        self.assertEqual(arg1.value, 'bar1')
        self.assertEqual(arg2.value, 'extra bar')
        self.assertEqual(arg.value, 'new value')
        self.assertEqual(arg.org_value, 'bar2')


if __name__ == '__main__':
    unittest.main()
