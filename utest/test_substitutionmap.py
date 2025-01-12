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
from robotmbt.substitutionmap import Constraint, SubstitutionMap

class TestConstraint(unittest.TestCase):
    def test_constraint_can_be_created_from_list_like_object(self):
        c = Constraint(('one', 'two', 'three'))
        self.assertIsInstance(c, Constraint)
        self.assertIsInstance(Constraint(['one', 'two', 'three']), Constraint)
        self.assertIsInstance(Constraint([1, 2, 3]), Constraint)
        self.assertIsInstance(Constraint(c), Constraint)

    def test_constraint_cannot_be_created_without_any_options(self):
        self.assertRaises(ValueError, Constraint, None)
        self.assertRaises(ValueError, Constraint, [])

    def test_constraint_cannot_be_created_from_single_object(self):
        self.assertRaises(ValueError, Constraint, 'one')
        self.assertRaises(ValueError, Constraint, 1)
        self.assertRaises(ValueError, Constraint, object())

    def test_additional_constraints_limit_available_choices(self):
        c = Constraint(['one', 'two', 'three'])
        self.assertEqual(len(c.optionset), 3)
        c.add_constraint(['one', 'two'])
        self.assertEqual(len(c.optionset), 2)
        c.add_constraint(['one', 'three'])
        self.assertEqual(len(c.optionset), 1)

    def test_available_options_can_be_reviewed(self):
        c = Constraint(['one', 'two', 'three'])
        for e in ['one', 'two', 'three']: self.assertIn(e, [opt for opt in c])
        c.add_constraint(['one', 'two'])
        for e in ['one', 'two']: self.assertIn(e, [opt for opt in c])
        self.assertNotIn('three', [opt for opt in c])
        c.add_constraint(['one', 'three'])
        for e in ['one']: self.assertIn(e, [opt for opt in c])
        for e in ['two', 'three']: self.assertNotIn(e, [opt for opt in c])

    def test_removing_last_choice_yields_exception(self):
        c = Constraint(['one', 'two', 'three'])
        self.assertRaises(ValueError, c.add_constraint, ['four', 'five'])
        self.assertRaises(ValueError, c.add_constraint, [])
        c = Constraint(['one', 'two', 'three'])
        c.add_constraint(['two', 'three'])
        c.add_constraint(['one', 'two'])
        self.assertRaises(ValueError, c.add_constraint, ['one', 'three'])

    def test_adding_none_constraint_keeps_current_options(self):
        c = Constraint(['one', 'two', 'three'])
        self.assertEqual(len(c.optionset), 3)
        options = [opt for opt in c]
        c.add_constraint(None)
        self.assertEqual(len(c.optionset), 3)
        self.assertEqual(options, [opt for opt in c])

    def test_constraint_copies_are_independent(self):
        c = Constraint(['one', 'two', 'three', 'thirteen'])
        c.add_constraint(['one', 'two', 'three'])
        cc = c.copy()
        self.assertEqual(len(c.optionset), 3)
        self.assertEqual(len(cc.optionset), 3)
        c.add_constraint(['one', 'two'])
        cc.add_constraint(['two', 'three'])
        self.assertEqual(len(c.optionset), 2)
        self.assertEqual(len(cc.optionset), 2)
        self.assertIn('two', c.optionset)
        self.assertIn('two', cc.optionset)
        self.assertNotIn('three', c.optionset)
        self.assertNotIn('one', cc.optionset)
