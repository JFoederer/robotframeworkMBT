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
from unittest.mock import patch

from types import SimpleNamespace

from robotmbt.suitedata import Suite, Scenario, Step


class TestSuites(unittest.TestCase):
    def setUp(self):
        self.topsuite = Suite('topsuite')
        self.topsuite.scenarios = [
            TestScenarios.create_scenario('scenario top A', self.topsuite),
            TestScenarios.create_scenario('scenario top B', self.topsuite)]
        subsuiteA = Suite('suite A', parent=self.topsuite)
        subsuiteA.scenarios = [TestScenarios.create_scenario('scenario AA', subsuiteA),
                               TestScenarios.create_scenario('scenario AB', subsuiteA)]
        subsuiteB = Suite('suite B', parent=self.topsuite)
        subsuiteB.scenarios = [TestScenarios.create_scenario('scenario BA', subsuiteB),
                               TestScenarios.create_scenario('scenario BB', subsuiteB)]
        self.topsuite.suites = [subsuiteA, subsuiteB]

    def test_suite_name(self):
        self.assertEqual(self.topsuite.name, 'topsuite')
        self.assertEqual(self.topsuite.suites[0].name, 'suite A')

    def test_longname_without_parent_is_just_the_name(self):
        self.assertEqual(self.topsuite.longname, self.topsuite.name)

    def test_longname_with_parent_includes_all_parent_names(self):
        self.assertEqual(self.topsuite.suites[0].scenarios[0].longname,
                         'topsuite.suite A.scenario AA')
        self.assertEqual(self.topsuite.suites[-1].scenarios[-1].longname,
                         'topsuite.suite B.scenario BB')

    def test_error_in_suite_setup_is_detected(self):
        step = Step('top setup', parent=self.topsuite)
        step.gherkin_kw = 'given'
        step.model_info = dict(error='oops')
        self.topsuite.setup = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [self.topsuite.setup])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_scenario_is_detected(self):
        self.topsuite.scenarios[0].steps[1].model_info = dict(error='oops')
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(len(errorsteps), 1)
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_suite_teardown_is_detected(self):
        step = Step('top teardown', parent=self.topsuite)
        step.model_info = dict(error='oops')
        self.topsuite.teardown = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [self.topsuite.teardown])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_subsuite_setup_is_detected(self):
        suite = self.topsuite.suites[0]
        step = Step('sub suite setup', parent=suite)
        step.gherkin_kw = 'given'
        step.model_info = dict(error='oops')
        suite.setup = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [suite.setup])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_subsuite_scenario_is_detected(self):
        self.topsuite.suites[0].scenarios[0].steps[1].model_info = dict(error='oops')
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(len(errorsteps), 1)
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_subsuite_teardown_is_detected(self):
        suite = self.topsuite.suites[0]
        step = Step('sub suite teardown', parent=suite)
        step.model_info = dict(error='oops')
        suite.teardown = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [suite.teardown])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_subscenario_setup_is_detected(self):
        scenario = self.topsuite.suites[0].scenarios[0]
        step = Step("sub suite's scenario teardown", parent=scenario)
        step.model_info = dict(error='oops')
        scenario.setup = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [scenario.setup])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_error_in_subscenario_teardown_is_detected(self):
        scenario = self.topsuite.suites[0].scenarios[1]
        step = Step("sub suite's scenario teardown", parent=scenario)
        step.model_info = dict(error='oops')
        scenario.teardown = step
        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(errorsteps, [scenario.teardown])
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')

    def test_multiple_errors_are_listed(self):
        step = Step('top setup', parent=self.topsuite)
        step.gherkin_kw = 'given'
        step.model_info = dict(error='setup oops')
        self.topsuite.setup = step
        self.topsuite.scenarios[0].steps[1].model_info =\
            dict(error='scenario oops')
        self.topsuite.suites[0].scenarios[0].steps[1].model_info =\
            dict(error='sub scenario oops')
        step = Step('sub teardown', parent=self.topsuite)
        step.model_info = dict(error='sub teardown oops')
        self.topsuite.suites[0].scenarios[0].setup = step

        self.assertIs(self.topsuite.has_error(), True)
        errorsteps = self.topsuite.steps_with_errors()
        self.assertEqual(len(errorsteps), 4)
        self.assertEqual(set([e.model_info['error'] for e in errorsteps]),
                         {'setup oops', 'scenario oops', 'sub scenario oops', 'sub teardown oops'})


class TestScenarios(unittest.TestCase):
    def setUp(self):
        self.scenario = self.create_scenario('My scenario')

    @staticmethod
    def create_scenario(name, parent=None):
        scenario = Scenario(name, parent)
        scenario.steps = TestSteps.create_steps(parent=scenario)
        return scenario

    def test_longname_without_parent_is_just_the_name(self):
        self.assertEqual(self.scenario.longname, self.scenario.name)

    def test_longname_with_parent_includes_both_names(self):
        def p(): return None  # Create an object to assign the name attribute to
        p.longname = 'long'
        scenario = Scenario('name', p)
        self.assertEqual(scenario.longname, 'long.name')

    def test_no_errors_when_ok(self):
        self.assertIs(self.scenario.has_error(), False)
        self.assertEqual(self.scenario.steps_with_errors(), [])

    def test_step_errors_are_reported(self):
        self.scenario.steps[0].model_info = dict(error='oops')
        self.assertIs(self.scenario.has_error(), True)
        errorsteps = self.scenario.steps_with_errors()
        self.assertEqual(len(errorsteps), 1)
        self.assertEqual(errorsteps[0].model_info['error'], 'oops')
        self.scenario.steps[1].model_info = dict(error='oh ow')
        self.assertIs(self.scenario.has_error(), True)
        errorsteps = self.scenario.steps_with_errors()
        self.assertEqual(len(errorsteps), 2)
        self.assertEqual([s.model_info['error'] for s in errorsteps], ['oops', 'oh ow'])

    def test_by_default_setup_and_teardown_are_empty(self):
        self.assertIs(self.scenario.setup, None)
        self.assertIs(self.scenario.teardown, None)

    def test_setup_errors(self):
        step = Step('my setup', parent=self.scenario)
        step.model_info = dict(error='oops')
        self.scenario.setup = step
        self.assertIs(self.scenario.has_error(), True)
        self.assertEqual(self.scenario.steps_with_errors(), [self.scenario.setup])

    def test_teardown_errors(self):
        step = Step('my teardown', parent=self.scenario)
        step.model_info = dict(error='oops')
        self.scenario.teardown = step
        self.assertIs(self.scenario.has_error(), True)
        self.assertEqual(self.scenario.steps_with_errors(), [self.scenario.teardown])

    def test_combined_errors(self):
        setup_step = Step('my setup', parent=self.scenario)
        setup_step.model_info = dict(error='oops in setup')
        self.scenario.setup = setup_step
        teardown_step = Step('my teardown', parent=self.scenario)
        teardown_step.model_info = dict(error='oops in teardown')
        self.scenario.teardown = teardown_step
        self.scenario.steps[0].model_info = dict(error='oops in scenario 1')
        self.scenario.steps[7].model_info = dict(error='oops in scenario 2')
        self.assertIs(self.scenario.has_error(), True)
        errorsteps = self.scenario.steps_with_errors()
        self.assertEqual(len(errorsteps), 4)
        self.assertEqual([e.model_info['error'] for e
                          in self.scenario.steps_with_errors()],
                         ['oops in setup',
                          'oops in scenario 1', 'oops in scenario 2',
                          'oops in teardown'])

    def test_scenarios_can_be_split(self):
        head, tail = self.scenario.split_at_step(4)
        self.assertEqual(head.steps, self.scenario.steps[:4])
        self.assertEqual(tail.steps, self.scenario.steps[4:])

    def test_split_keeps_setup_and_teardown_at_the_edges(self):
        self.scenario.setup = 'before'
        self.scenario.teardown = 'after'
        head, tail = self.scenario.split_at_step(4)
        self.assertIs(head.setup, 'before')
        self.assertIs(head.teardown, None)
        self.assertIs(tail.setup, None)
        self.assertIs(tail.teardown, 'after')

    def test_split_scenarios_keep_their_parent(self):
        head, tail = self.scenario.split_at_step(4)
        self.assertIs(head.parent, self.scenario.parent)
        self.assertIs(tail.parent, self.scenario.parent)

    def test_scenarios_can_be_split_before_first_step(self):
        head, tail = self.scenario.split_at_step(0)
        self.assertEqual(head.steps, [])
        self.assertEqual(tail.steps, self.scenario.steps)

    def test_scenarios_can_be_split_after_last_step(self):
        head, tail = self.scenario.split_at_step(10)
        self.assertEqual(head.steps, self.scenario.steps)
        self.assertEqual(tail.steps, [])

    def test_split_scenario_from_the_back(self):
        head, tail = self.scenario.split_at_step(-2)
        self.assertEqual(head.steps, self.scenario.steps[:8])
        self.assertEqual(tail.steps, self.scenario.steps[8:])
        head, tail = self.scenario.split_at_step(-8)
        self.assertEqual(head.steps, self.scenario.steps[:2])
        self.assertEqual(tail.steps, self.scenario.steps[2:])

    def test_split_fails_on_invlaid_stepindex(self):
        self.assertRaises(AssertionError, self.scenario.split_at_step, 11)

    def test_copies_are_independent(self):
        dup = self.scenario.copy()
        dup.name = "other name"
        dup.steps.append(Step('extra step', parent=dup))
        self.assertIs(dup.parent, self.scenario.parent)
        self.assertEqual(dup.setup, self.scenario.setup)
        self.assertEqual(dup.teardown, self.scenario.teardown)
        self.assertNotEqual(dup.name, self.scenario.name)
        self.assertIsNot(dup.steps[0], self.scenario.steps[0])
        self.assertEqual(dup.steps[0].keyword, self.scenario.steps[0].keyword)
        self.assertNotEqual(dup.steps[-1].keyword, self.scenario.steps[-1].keyword)

    def test_exteranally_determined_attributes_are_copied_along(self):
        self.scenario.src_id = 7

        class Dummy:
            def copy(self):
                return 'dummy'
        self.scenario.data_choices = Dummy()
        dup = self.scenario.copy()
        self.assertEqual(dup.src_id, self.scenario.src_id)
        self.assertEqual(dup.data_choices, 'dummy')


@patch('robotmbt.suitedata.ArgumentValidator')
class TestSteps(unittest.TestCase):
    def setUp(self):
        self.steps = self.create_steps()

    @staticmethod
    def create_steps(parent=None):
        Kw1 = Step('action keyword', parent=parent)
        Gg1 = Step('Given step Gg1', parent=parent)
        Ga1 = Step('and step Ga1', parent=parent)
        Gb1 = Step('but step Gb1', parent=parent)
        Gg1.gherkin_kw = Ga1.gherkin_kw = Gb1.gherkin_kw = 'given'
        Ww1 = Step('When step Ww1', parent=parent)
        Wa1 = Step('and step Wa1', parent=parent)
        Wb1 = Step('BUT step Wb1', parent=parent)
        Ww1.gherkin_kw = Wa1.gherkin_kw = Wb1.gherkin_kw = 'when'
        Tt1 = Step('Then step Tt1', parent=parent)
        Ta1 = Step('And step Ta1', parent=parent)
        Tb1 = Step('but step Tb1', parent=parent)
        Tt1.gherkin_kw = Ta1.gherkin_kw = Tb1.gherkin_kw = 'then'
        return [Kw1, Gg1, Ga1, Gb1, Ww1, Wa1, Wb1, Tt1, Ta1, Tb1]

    def test_full_names(self, mock):
        expected = ['action keyword',
                    'Given step Gg1',
                    'and step Ga1',
                    'but step Gb1',
                    'When step Ww1',
                    'and step Wa1',
                    'BUT step Wb1',
                    'Then step Tt1',
                    'And step Ta1',
                    'but step Tb1']
        for s, e in zip(self.steps, expected):
            self.assertEqual(s.keyword, e)
            self.assertEqual(str(s), e)

    def test_gherkin_keywords(self, mock):
        expected = [None] + 3*['given'] + 3*['when'] + 3*['then']
        for s, e in zip(self.steps, expected):
            self.assertEqual(s.gherkin_kw, e)

    def test_gherkin_keywords_are_lower_case(self, mock):
        source = [None, 'given', 'Given', 'GIVEN',
                        'wHEN', 'wHEn',  'WHEn',
                        'TheN', 'theN',  'thEN']
        expected = [None] + 3*['given'] + 3*['when'] + 3*['then']
        for s, gkw in zip(self.steps, source):
            s.gherkin_kw = gkw
        for s, e in zip(self.steps, expected):
            self.assertEqual(s.gherkin_kw, e)

    def test_step_keywords_are_kept_as_is(self, mock):
        expected = [None, 'Given', 'and', 'but',
                          'When', 'and', 'BUT',
                          'Then', 'And', 'but']
        for s, e in zip(self.steps, expected):
            self.assertEqual(s.step_kw, e)

    def test_keywords_are_available_without_their_gherkin_keyword(self, mock):
        expected = ['action keyword', 'step Gg1', 'step Ga1', 'step Gb1',
                                      'step Ww1', 'step Wa1', 'step Wb1',
                                      'step Tt1', 'step Ta1', 'step Tb1']
        for s, e in zip(self.steps, expected):
            self.assertEqual(s.kw_wo_gherkin, e)

    def test_embedded_arguments_are_part_of_the_step_str(self, mock):
        step = Step(RobotKwStub.STEPTEXT, parent=None)
        self.assertEqual(str(step), RobotKwStub.STEPTEXT)
        step.add_robot_dependent_data(RobotKwStub())
        self.assertNotIn('error', step.model_info)
        self.assertEqual(str(step), RobotKwStub.STEPTEXT)

    def test_modified_embedded_arguments_are_part_of_the_step_str(self, mock):
        step = Step(RobotKwStub.STEPTEXT, parent=None)
        self.assertEqual(str(step), RobotKwStub.STEPTEXT)
        step.add_robot_dependent_data(RobotKwStub())
        self.assertNotIn('error', step.model_info)
        step.args['${bar}'].value = 'new bar'
        self.assertEqual(str(step), RobotKwStub.STEPTEXT.replace('bar_value', 'new bar'))

    def test_all_arguments_are_part_of_the_full_keyword_text(self, mock):
        step = Step(RobotKwStub.STEPTEXT, 'posA', 'pos2=posB', 'named1=namedA', parent=None)
        self.assertEqual(step.full_keyword, f"{RobotKwStub.STEPTEXT}    posA    pos2=posB    named1=namedA")

    def test_return_value_assignment_is_part_of_the_full_keyword_text(self, mock):
        step = Step(RobotKwStub.STEPTEXT, assign=('${output}',), parent=None)
        self.assertEqual(step.full_keyword, "${output}    " + RobotKwStub.STEPTEXT)

    def test_return_value_assignment_with_eq_is_part_of_the_full_keyword_text(self, mock):
        step = Step(RobotKwStub.STEPTEXT, assign=('${output}=',), parent=None)
        self.assertEqual(step.full_keyword, "${output}=    " + RobotKwStub.STEPTEXT)

    def test_return_value_assignment_with_eq_after_space_is_part_of_the_full_keyword_text(self, mock):
        step = Step(RobotKwStub.STEPTEXT, assign=('${output} =',), parent=None)
        self.assertEqual(step.full_keyword, "${output} =    " + RobotKwStub.STEPTEXT)

    def test_return_value_multi_assignment_is_part_of_the_full_keyword_text(self, mock):
        step = Step(RobotKwStub.STEPTEXT, assign=('${output1}', '${output2}='), parent=None)
        self.assertEqual(step.full_keyword, "${output1}    ${output2}=    " + RobotKwStub.STEPTEXT)

    def test_argument_with_default_is_omitted_from_keyword_when_not_mentioned_named(self, mock):
        step = Step(RobotKwStub.STEPTEXT, 'posA', 'pos2=posB', parent=None)
        step.args = StubStepArguments([StubArgument(name='pos1',   value='posA',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='pos2',   value='posB',   is_default=False, kind='NAMED'),
                                       StubArgument(name='named1', value='namedA', is_default=True,  kind='NAMED')])
        self.assertTupleEqual(step.posnom_args_str, ('posA', 'pos2=posB'))
        self.assertEqual(step.full_keyword, f"{RobotKwStub.STEPTEXT}    posA    pos2=posB")

    def test_argument_with_default_is_omitted_from_keyword_when_not_mentioned_positional(self, mock):
        step = Step(RobotKwStub.STEPTEXT, 'posA', 'posB', parent=None)
        step.args = StubStepArguments([StubArgument(name='pos1',   value='posA',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='pos2',   value='posB',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='named1', value='namedA', is_default=True,  kind='POSITIONAL')])
        self.assertTupleEqual(step.posnom_args_str, ('posA', 'posB'))
        self.assertEqual(step.full_keyword, f"{RobotKwStub.STEPTEXT}    posA    posB")

    def test_argument_with_default_is_included_in_keyword_when_mentioned_named(self, mock):
        step = Step(RobotKwStub.STEPTEXT, 'posA', 'pos2=posB', 'named1=namedA', parent=None)
        step.args = StubStepArguments([StubArgument(name='pos1',   value='posA',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='pos2',   value='posB',   is_default=False, kind='NAMED'),
                                       StubArgument(name='named1', value='namedA', is_default=False, kind='NAMED')])
        self.assertTupleEqual(step.posnom_args_str, ('posA', 'pos2=posB', 'named1=namedA'))
        self.assertEqual(step.full_keyword, f"{RobotKwStub.STEPTEXT}    posA    pos2=posB    named1=namedA")

    def test_argument_with_default_is_included_in_keyword_when_mentioned_positional(self, mock):
        step = Step(RobotKwStub.STEPTEXT, 'posA', 'posB', 'namedA', parent=None)
        step.args = StubStepArguments([StubArgument(name='pos1',   value='posA',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='pos2',   value='posB',   is_default=False, kind='POSITIONAL'),
                                       StubArgument(name='named1', value='namedA', is_default=False, kind='POSITIONAL')])
        self.assertTupleEqual(step.posnom_args_str, ('posA', 'posB', 'namedA'))
        self.assertEqual(step.full_keyword, f"{RobotKwStub.STEPTEXT}    posA    posB    namedA")

    def test_positional_and_named_arguments_are_available_in_robot_tuple_format(self, mock):
        argtuple = 'posA', 'pos2=posB', 'named1=namedA'
        step = Step(RobotKwStub.STEPTEXT, *argtuple, parent=None)
        self.assertTupleEqual(step.posnom_args_str, argtuple)

    def test_keyword_errors_become_model_errors(self, mock):
        step = Step(RobotKwStub.STEPTEXT, parent=None)
        kw = RobotKwStub()
        kw.error = 'keyword error'
        step.add_robot_dependent_data(kw)
        self.assertEqual(step.model_info['error'], 'keyword error')

    def test_model_info_is_loaded(self, mock):
        step = Step(RobotKwStub.STEPTEXT, parent=None)
        kw = RobotKwStub()
        kw._doc = """*model info*
                     :IN:  expr1 | expr2
                     :OUT: expr3 | expr4
                  """
        step.add_robot_dependent_data(kw)
        self.assertEqual(step.model_info, dict(IN=['expr1', 'expr2'],
                                               OUT=['expr3', 'expr4']))

    def test_model_info_errors_are_reported(self, mock):
        step = Step(RobotKwStub.STEPTEXT, parent=None)
        kw = RobotKwStub()
        kw._doc = """*model info*
                     :INVALID
                  """
        step.add_robot_dependent_data(kw)
        self.assertIn('error', step.model_info)


class RobotKwStub:
    STEPTEXT = "Given step with foo_value and bar_value as arguments"

    def __init__(self):
        self.name = "step with ${foo} and ${bar} as arguments"
        self._doc = "*model info*\n:IN: None\n:OUT: None"
        self.args = self.argstub()
        self.error = False
        self.embedded = SimpleNamespace(args=['${foo}', '${bar}'],
                                        parse_args=lambda _: ['foo_value', 'bar_value'])

    class argstub:
        argument_names = []
        def map(x, y, z): return ([], [])
        def __iter__(_): return iter([])


class StubStepArguments(list):
    modified = True  # trigger modified status to get arguments processed, rather then just echoed


class StubArgument(SimpleNamespace):
    EMBEDDED = 'EMBEDDED'
    POSITIONAL = 'POSITIONAL'
    VAR_POS = 'VAR_POS'
    NAMED = 'NAMED'
    FREE_NAMED = 'FREE_NAMED'



class StubStepArguments(list):
    modified = True # trigger modified status to get arguments processed, rather then just echoed


class StubArgument(SimpleNamespace):
    EMBEDDED = 'EMBEDDED'
    POSITIONAL = 'POSITIONAL'
    VAR_POS = 'VAR_POS'
    NAMED = 'NAMED'
    FREE_NAMED = 'FREE_NAMED'


if __name__ == '__main__':
    unittest.main()
