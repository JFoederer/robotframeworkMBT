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

class TestModelSpace(unittest.TestCase):
    def setUp(self):
        self.m = ModelSpace()

    def test_create_modelspace(self):
        self.assertIsInstance(self.m, ModelSpace)

    def test_add_property(self):
        self.m.add_prop('foo')
        self.assertIn('foo', dir(self.m))

    def test_delete_property(self):
        self.m.add_prop('foo')
        self.assertIn('foo', dir(self.m))
        self.m.del_prop('foo')
        self.assertNotIn('foo', dir(self.m))

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

    def test_fail_when_comparing_undefined_name(self):
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('foo.bar == foobar')
        self.assertEqual(str(cm.exception), "bar used before assignment")

    def test_fail_when_comparing_unknown_property(self):
        self.m.add_prop('foo')
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('foo.bar == foobar')
        self.assertEqual(str(cm.exception), "bar used before assignment")
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('foo.bar.foobar = 13')
        self.assertEqual(str(cm.exception), "bar used before assignment")

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

    def test_list_attribute(self):
        self.m.add_prop('foo')
        self.m.process_expression('foo.bar = [1, 2, 3]')
        self.m.process_expression('foo.bar.append(4)')
        self.assertEqual(self.m.get_status_text(), "foo:\n"
                                                   "    bar=[1, 2, 3, 4]\n")

    def test_list_attribute_with_model_references(self):
        self.m.add_prop('foo1')
        self.m.add_prop('foo2')
        self.m.add_prop('foolist')
        self.m.process_expression('foolist.bar = [foo1]')
        self.m.process_expression('foolist.bar.append(foo2)')
        self.assertEqual(self.m.get_status_text(), "foo1:\n"
                                                   "foo2:\n"
                                                   "foolist:\n"
                                                   "    bar=[foo1, foo2]\n")

    def test_string_attributes(self):
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = "foobar"')
        self.assertIs(self.m.process_expression('foo.bar == "foobar"'), True)

    def test_introducing_named_attribute_from_statement(self):
        """
        Here the quotes are removed from the assignment statement. Statements and
        expressions need to be handled differently. Evaluating 'foo.bar = foobar' as an
        expression would yield a SyntaxError on the assignment, before getting to the
        NameError on foobar.
        """
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = foobar')
        self.assertIs(self.m.process_expression('foo.bar == foobar'), True)

    def test_introducing_named_attribute_from_expression(self):
        """
        Just like `foo.bar = foobar` is an assignment where this is foobar's first use,
        a name can also be introduced in an append. The difference is that the former is
        a statement, the latter an expression.
        """
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = []')
        self.m.process_expression('foo.bar.append(bar1)')
        self.assertIs(self.m.process_expression('bar1 in foo.bar'), True)

    def test_nested_attributes(self):
        self.m.process_expression('new foo1')
        self.m.process_expression('foo1.add_prop(bar1)')
        self.m.process_expression('foo1.bar1.foo2 = barbar')
        self.m.process_expression('foo1.bar1.foo3 = barbar')
        self.assertIs(self.m.process_expression('foo1.bar1.foo2 == foo1.bar1.foo3'), True)

    def test_fail_on_naming_conflict_property_exists(self):
        self.m.process_expression('new foo1')
        self.assertRaises(ModellingError, self.m.process_expression, 'new foo1')

    def test_fail_on_naming_conflict_literal_exists(self):
        self.m.process_expression('new foo1')
        self.m.process_expression('foo1.bar = foo2')
        self.assertRaises(ModellingError, self.m.process_expression, 'new foo2')

    def test_list_comprehension_name_error(self):
        """
        Some weird quirk in Python causes list comprehensions which are used as a
        generator expression to be executed in their own local scope. The scenario
        in this test would cause a NameError on A, due to the underlying code using
        Python's eval() and exec() functions, without passing the scope explicitly.

        https://docs.python.org/3/reference/executionmodel.html#interaction-with-dynamic-features
        """
        self.m.process_expression('new foo')
        self.m.process_expression("foo.bar = ['A', 'B', 'C']")
        self.assertIs(self.m.process_expression("any(elm == A for elm in foo.bar)"), True)

    def test_fail_exists_check_before_using_new(self):
        self.assertRaises(NameError, self.m.process_expression, 'foo')

    def test_fail_exists_check_before_using_new_with_stripping(self):
        self.assertRaises(NameError, self.m.process_expression, ' foo ')

    def test_fail_exists_check_after_using_del(self):
        self.m.process_expression('new foo')
        self.assertIn('foo', dir(self.m))
        self.m.process_expression('del foo')
        self.assertRaises(NameError, self.m.process_expression, 'foo')

    def test_del_fails_if_property_does_not_exist(self):
        self.assertRaises(ModellingError, self.m.process_expression, 'del foo')

    def test_copies_have_all_data(self):
        self.m.process_expression('new foo1')
        self.m.process_expression('foo1.bar = foobar1')
        self.m.process_expression('new foo2')
        self.m.process_expression('foo2.bar = foobar2')
        m_copy = self.m.copy()
        m_copy.process_expression('foo1.bar = foobar1')
        m_copy.process_expression('foo2.bar = foobar2')

    def test_copies_are_independent(self):
        self.m.process_expression('new foo')
        self.m.process_expression('foo.bar = foobar')
        m_copy = self.m.copy()
        m_copy.process_expression('foo.bar = raboof')
        self.assertIs(self.m.process_expression('foo.bar == foobar'), True)
        self.assertIs(m_copy.process_expression('foo.bar == raboof'), True)

        self.m.process_expression('new foo2')
        self.m.process_expression('foo2.bar = foobar2')
        m_copy.process_expression('new foo3')
        m_copy.process_expression('foo3.bar = foobar3')
        self.assertRaises(NameError, m_copy.process_expression, 'foo2')
        self.assertIs(m_copy.process_expression('foo3.bar == foobar3'), True)

    def test_equal_operator(self):
        m1 = ModelSpace()
        m2 = ModelSpace()
        self.assertTrue(m1 == m2)
        for action in ['new foo1', 'foo1.bar1 = foobar1', 'foo1.bar2 = foobar2',
                       'new foo2', 'foo2.bar1 = foobar1', 'foo2.bar2 = foobar2', 'del foo2']:
            m1.process_expression(action)
            m2.process_expression(action)
            self.assertTrue(m1 == m2)
        m2.process_expression('foo1.bar1 = 13')
        self.assertFalse(m1 == m2)


class TestScenarioScopeVars(unittest.TestCase):
    def setUp(self):
        self.m = ModelSpace()

    def test_scenario_scope_var_cannot_be_user_defined(self):
        self.assertRaises(ModellingError, self.m.process_expression, 'new scenario')

    def test_scenario_scope_var_cannot_be_user_removed(self):
        self.assertRaises(ModellingError, self.m.process_expression, 'del scenario')

    def test_initial_scenario_scope_cannot_be_ended(self):
        self.assertRaises(AssertionError, self.m.end_scenario_scope)
        self.m.new_scenario_scope()
        self.m.end_scenario_scope()
        self.assertRaises(AssertionError, self.m.end_scenario_scope)

    def test_scenario_scope_is_unavailable_outside_scenarios(self):
        self.assertRaises(NameError, self.m.process_expression, 'scenario')
        self.assertRaises(ModellingError, self.m.process_expression, 'scenario.foo = bar')
        self.m.new_scenario_scope()
        self.m.end_scenario_scope()
        self.assertRaises(NameError, self.m.process_expression, 'scenario')
        self.assertRaises(ModellingError, self.m.process_expression, 'scenario.foo = bar')

    def test_scenario_scope_is_available_inside_scenarios(self):
        self.m.new_scenario_scope()
        self.assertIsNotNone(self.m.process_expression('scenario'))
        self.m.process_expression('scenario.foo = bar')
        self.assertEqual(self.m.process_expression('scenario.foo'), 'bar')

    def test_scenario_used_as_literal(self):
        self.m.process_expression('new foo')
        self.assertRaises(ModellingError, self.m.process_expression, 'foo.bar = scenario')
        self.m.process_expression('foo.bar = "scenario"')
        self.assertEqual(self.m.process_expression('foo.bar'), "scenario")

    def test_scenario_used_as_attribute_name(self):
        self.m.process_expression('new foo')
        self.m.process_expression('foo.scenario = bar')
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.assertEqual(self.m.process_expression('scenario.foo'), self.m.process_expression('foo.scenario'))

    def test_scenario_var_is_unavailable_outside_scenario(self):
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.m.end_scenario_scope()
        self.assertRaises(ModellingError, self.m.process_expression, 'scenario.bar == bar')
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('scenario.bar == bar')
        self.assertIsInstance(cm.exception, ModellingError)
        self.assertTrue(str(cm.exception).startswith("Accessing scenario scope while there is no scenario active"))

    def test_scenario_var_is_unavailable_in_next_scenario(self):
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.m.end_scenario_scope()
        self.m.new_scenario_scope()
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('scenario.bar == bar')
        self.assertIsInstance(cm.exception, ModellingError)
        self.assertEqual(str(cm.exception), "bar used before assignment")

    def test_scenario_var_is_available_in_nested_scope(self):
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.m.new_scenario_scope()
        self.assertEqual(self.m.process_expression('scenario.foo'), 'bar')

    def test_scenario_var_can_be_modified_inside_nested_scope(self):
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.m.new_scenario_scope()
        self.assertEqual(self.m.process_expression('scenario.foo'), 'bar')
        self.m.process_expression('scenario.foo = barbar')
        self.assertEqual(self.m.process_expression('scenario.foo'), 'barbar')

    def test_scenario_var_modification_from_nested_scope_is_visible_in_outer_scope(self):
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.m.new_scenario_scope()
        self.assertEqual(self.m.process_expression('scenario.foo'), 'bar')
        self.m.process_expression('scenario.foo = barbar')
        self.m.end_scenario_scope()
        self.assertEqual(self.m.process_expression('scenario.foo'), 'barbar')

    def test_new_scenario_var_from_nested_scope_is_unavailable_in_outer_scope(self):
        self.m.new_scenario_scope()
        self.m.new_scenario_scope()
        self.m.process_expression('scenario.foo = bar')
        self.assertTrue(self.m.process_expression('scenario.foo == bar'))
        self.m.end_scenario_scope()
        with self.assertRaises(ModellingError) as cm:
            self.m.process_expression('scenario.foo == bar')
        self.assertIsInstance(cm.exception, ModellingError)
        self.assertEqual(str(cm.exception), "foo used before assignment")


if __name__ == '__main__':
    unittest.main()
