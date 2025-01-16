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


class TestSubstitutionMap(unittest.TestCase):
    def test_an_empty_substitution_map_yields_an_empty_solution(self):
        sm = SubstitutionMap()
        self.assertEqual(sm.solve(), {})
        self.assertEqual(sm.solution, {})

    def test_single_distinct_options_are_the_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1])
        sm.substitute('B', [2])
        self.assertEqual(sm.solve(), {'A':1, 'B':2})
        self.assertEqual(sm.solution, {'A':1, 'B':2})

    def test_single_overlapping_options_have_no_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1])
        sm.substitute('B', [1])
        self.assertRaises(ValueError, sm.solve)

    def test_multi_overlapping_options_have_no_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3])
        sm.substitute('B', [1])
        sm.substitute('C', [2])
        sm.substitute('D', [3])
        self.assertRaises(ValueError, sm.solve)

    def test_each_example_value_gets_a_unique_solution_value(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3])
        sm.substitute('B', [1, 2, 3])
        sm.substitute('C', [1, 2, 3])
        sm.solve()
        self.assertNotEqual(sm.solution['A'], sm.solution['B'])
        self.assertNotEqual(sm.solution['A'], sm.solution['C'])
        self.assertNotEqual(sm.solution['B'], sm.solution['C'])

    def test_adding_new_constraint_clears_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        sm.solve()
        self.assertNotEqual(sm.solution, {})
        sm.substitute('B', [1, 2])
        self.assertEqual(sm.solution, {})
        sm.solve()
        self.assertNotEqual(sm.solution, {})
        sm.substitute('B', [1])
        self.assertEqual(sm.solution, {})

    def test_removing_last_option_in_substitution_raises(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3])
        self.assertRaises(ValueError, sm.substitute, 'A', [8, 9])
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3])
        self.assertRaises(ValueError, sm.substitute, 'A', [])

    def test_failing_to_solve_clears_prior_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1])
        sm.substitute('B', [1, 2])
        sm.solve()
        self.assertNotEqual(sm.solution, {})
        sm.substitute('B', [1])
        self.assertRaises(ValueError, sm.solve)
        self.assertEqual(sm.solution, {})

    def test_wrong_choice_blocks_solution(self):
        """
        If 2 is chosen as the solution value for A, before evaluating
        B and C, then either B or C can still be solved, but not both.
        """
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        sm.substitute('B', [2, 3])
        sm.substitute('C', [2, 3])
        sm.solve()
        self.assertEqual(sm.solution['A'], 1)
        self.assertIn(sm.solution['B'], [2, 3])
        self.assertIn(sm.solution['C'], [2, 3])
        self.assertNotEqual(sm.solution['B'], sm.solution['C'])

    def test_wrong_choice_blocks_solution_repeated(self):
        """
        The 'wrong choice' test proved powerful, but due to randomisation
        it was still possible to get a passing test run, even though the
        implementation did not always find a solution. Repeating the test
        with varying data helps to detect randomisation flukes and
        algorithmic blind spots, like order preference.
        """
        variations = [{'A':[1, 2], 'B':[2, 3], 'C':[3, 2]},
                      {'A':[2, 1], 'B':[2, 3], 'C':[2, 3]},
                      {'A':[1, 2], 'B':[3, 2], 'C':[2, 3]},
                      {'A':[2, 1], 'B':[3, 2], 'C':[3, 2]},
                      {'A':[2, 3], 'B':[1, 2], 'C':[2, 3]},
                      {'A':[2, 3], 'B':[2, 3], 'C':[1, 2]},
                      {'A':[3, 2], 'B':[2, 1], 'C':[2, 3]},
                      {'A':[3, 2], 'B':[3, 2], 'C':[2, 1]}]
        for variant in variations:
            sm = SubstitutionMap()
            for example_value, constraint in variant.items():
                sm.substitute(example_value, constraint)
            sm.solve()
            the_one = [k for k, v in variant.items() if 1 in v][0]
            others = [k for k in variant if k != the_one]
            self.assertEqual(sm.solution[the_one], 1)
            self.assertIn(sm.solution[others[0]], [2, 3])
            self.assertIn(sm.solution[others[1]], [2, 3])
            self.assertNotEqual(sm.solution[others[0]], sm.solution[others[1]])

    def test_block_constraints_with_no_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3, 4])
        sm.substitute('B', [1, 2, 3, 4])
        sm.substitute('C', [1, 2, 3, 4])
        sm.substitute('D', [1, 2, 3, 4])
        sm.substitute('E', [1, 2, 3, 4])
        self.assertRaises(ValueError, sm.solve)

    def test_cascading_constraints_with_sigle_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1])
        sm.substitute('B', [1, 2])
        sm.substitute('C', [1, 2, 3])
        sm.substitute('D', [1, 2, 3, 4])
        sm.substitute('E', [1, 2, 3, 4, 5])
        sm.solve()
        self.assertEqual(sm.solution, dict(A=1, B=2, C=3, D=4, E=5))

    def test_reverse_cascading_constraints_with_single_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3, 4, 5])
        sm.substitute('B', [1, 2, 3, 4])
        sm.substitute('C', [1, 2, 3])
        sm.substitute('D', [1, 2])
        sm.substitute('E', [1])
        sm.solve()
        self.assertEqual(sm.solution, dict(A=5, B=4, C=3, D=2, E=1))

    def test_chained_constraints_with_single_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        sm.substitute('B', [2, 3])
        sm.substitute('C', [3, 4])
        sm.substitute('D', [4, 5])
        sm.substitute('E', [5])
        sm.solve()
        self.assertEqual(sm.solution, dict(A=1, B=2, C=3, D=4, E=5))

    def test_reversed_chained_constraints_with_single_solution(self):
        sm = SubstitutionMap()
        sm.substitute('A', [5])
        sm.substitute('B', [5, 4])
        sm.substitute('C', [4, 3])
        sm.substitute('D', [3, 2])
        sm.substitute('E', [2, 1])
        sm.solve()
        self.assertEqual(sm.solution, dict(A=5, B=4, C=3, D=2, E=1))

    def test_chained_constraints_with_two_solutions(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        sm.substitute('B', [2, 3])
        sm.substitute('C', [3, 4])
        sm.substitute('D', [4, 5])
        sm.substitute('E', [5, 1])
        result_options_found = 2*[False]
        while not all(result_options_found):
            sm.solve()
            if sm.solution['A'] == 1:
                self.assertEqual(sm.solution, dict(A=1, B=2, C=3, D=4, E=5))
                result_options_found[0] = True
            elif sm.solution['A'] == 2:
                self.assertEqual(sm.solution, dict(A=2, B=3, C=4, D=5, E=1))
                result_options_found[1] = True
            else:
                assert False, "Invalid solution generated"

    def test_substitution_map_copies_are_independent(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2, 3])
        sm.substitute('B', [1, 2, 3])
        sm.substitute('C', [1, 2, 3])
        sm.solve()
        sm2 = sm.copy()
        self.assertEqual(sm.solution, sm2.solution)
        self.assertIsNot(sm.solution, sm2.solution)
        # remove chosen value for C from sm2 and check that
        # substitutions and solution have their own values
        c_solution = sm.solution['C']
        sm2.substitute('C', [n for n in [1, 2, 3] if n != c_solution])
        sm2.solve()
        self.assertNotEqual(sm.solution, sm2.solution)
        self.assertIn(c_solution, sm.substitutions['C'])
        self.assertNotIn(c_solution, sm2.substitutions['C'])

    def test_substitution_map_str_without_solution_shows_all_possible_values(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        self.assertIn('A', f"{sm}")
        self.assertIn('1', f"{sm}")
        self.assertIn('2', f"{sm}")
        sm.substitute('B', [2, 3])
        self.assertIn('B', f"{sm}")
        self.assertIn('3', f"{sm}")
        self.assertEqual(f"{sm}".count('2'), 2)

    def test_substitution_map_str_with_solution_shows_results_only(self):
        sm = SubstitutionMap()
        sm.substitute('A', [1, 2])
        sm.substitute('B', [2, 3])
        sm.substitute('C', [2])
        self.assertEqual(f"{sm}".count('2'), 3)
        sm.solve()
        self.assertEqual(f"{sm}".count('2'), 1)


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

    def test_constraints_strip_duplicate_values(self):
        c = Constraint(['one', 'two', 'two', 'three'])
        self.assertEqual(len(c.optionset), 3)
        c.add_constraint(['two', 'two', 'three', 'three', 'four', 'four'])
        self.assertEqual(len(c.optionset), 2)
        self.assertSetEqual(c.optionset, set(['two', 'three']))

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
