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
from robotmbt.modelspace import ModelSpace, ModellingError

# To run unit tests:
#   * open a command prompt
#   * go to the robotframeworkMBT project root folder
#   * run: python -m unittest discover utest

class TestModelSpace(unittest.TestCase):
    def setUp(self):
        self.m = ModelSpace()

    def test_create_modelspace(self):
        self.assertIsInstance(self.m, ModelSpace)

    def test_add_property(self):
        self.m.add_prop('foo')
        self.assertIn('foo', dir(self.m))

    def test_try_add_same_property(self):
        self.m.add_prop('foo')
        self.assertRaises(ModellingError, self.m.add_prop, 'foo')

    def test_assign_property(self):
        self.m.add_prop('foo')
        self.m.process_expression('foo.bar = 13')
        self.assertIs(self.m.process_expression('foo.bar == 13'), True)

    def test_compare_property(self):
        self.m.add_prop('foo')
        self.m.process_expression('foo.bar = 13')
        self.assertIs(self.m.process_expression('foo.bar == 13'), True)
        self.assertIs(self.m.process_expression('foo.bar > 3'), True)

    def test_compare_property_false(self):
        self.m.add_prop('foo')
        self.m.process_expression('foo.bar = 13')
        self.assertFalse(self.m.process_expression('foo.bar > 1313'), True)

    def test_add_multiple_properties(self):
        self.m.add_prop('foo1')
        self.assertIn('foo1', dir(self.m))
        self.m.add_prop('foo2')
        self.assertIn('foo1', dir(self.m))
        self.assertIn('foo2', dir(self.m))

    def test_compare_multiple_properties(self):
        self.m.add_prop('foo1')
        self.m.process_expression('foo1.bar = 13')
        self.m.add_prop('foo2')
        self.m.process_expression('foo2.bar = 1313')
        self.assertIs(self.m.process_expression('foo1.bar == 13'), True)
        self.assertIs(self.m.process_expression('foo2.bar == 1313'), True)
        self.assertIs(self.m.process_expression('foo1.bar < foo2.bar'), True)

    def test_fail_when_comparing_unknown_property(self):
        self.m.add_prop('foo')
        self.assertRaises(AttributeError, self.m.process_expression, 'foo.bar == foobar')

    def test_statements_return_exec(self):
        self.m.add_prop('foo')
        self.assertEqual(self.m.process_expression('foo.bar = 13'), 'exec')

    def test_new_vocab(self):
        self.m.process_expression('new foo')
        self.assertIn('foo', dir(self.m))
        self.m.process_expression('foo.bar = 13')
        self.assertIs(self.m.process_expression('foo.bar == 13'), True)

    def test_property_exists(self):
        self.m.process_expression('new foo')
        self.assertTrue(self.m.process_expression('foo'))

    def test_get_status_text(self):
        self.m.add_prop('foo1')
        self.m.process_expression('foo1.bar = 13')
        self.m.add_prop('foo2')
        self.m.process_expression('foo2.bar = 1313')
        self.assertEqual(self.m.get_status_text(), "foo1:\n"
                                                   "    bar=13\n"
                                                   "foo2:\n"
                                                   "    bar=1313\n")

    def test_string_attributes(self):
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = "foobar"')
        self.assertIs(self.m.process_expression('foo.bar == "foobar"'), True)

    def test_assigning_named_attributes(self):
        """
        Named attributes of properties can be used without quotes. If expressions were
        processed as just a regular Python expression, it would fail on a NameError.
        """
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = foobar')
        self.assertIs(self.m.process_expression('foo.bar == foobar'), True)

    def test_fail_evaluating_named_attribute_before_assignment(self):
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = "foobar"')
        self.assertRaises(NameError, self.m.process_expression, 'foo.bar == foobar')

    def test_fail_on_naming_conflict(self):
        self.m.process_expression('new foo1')
        self.m.process_expression('foo1.bar = foo2')
        self.assertRaises(ModellingError, self.m.process_expression, 'new foo2')


if __name__ == '__main__':
    unittest.main()
