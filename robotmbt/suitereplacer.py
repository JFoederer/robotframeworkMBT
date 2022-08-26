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

from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import keyword
from robot.api import logger
import robot.running.model as rmodel

from .suiteprocessors import SuiteProcessors
from .suitedata import Suite, Scenario, Step
from .modelspace import ModelSpace

class SuiteReplacer:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, processor='process_test_suite', processor_lib=None,):
        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None
        self.robot_suite = None
        self.current_step = None
        suite_processor = SuiteProcessors() if processor_lib is None \
                                          else getattr(Robot.get_library_instance(processor_lib))
        self.suite_processor = getattr(suite_processor, processor)

    @keyword(name="Treat this test suite Model-based")
    def treat_model_based(self):
        """
        Iterate through the suite and if all keywords also have a modelling variant (prefix 'model')
        then replace the contents with a generated trace.
        """
        self.robot_suite = self.current_suite

        logger.info(f"Analysing Robot test suite '{self.robot_suite.name}' for model-based execution.")
        master_suite = self.__process_robot_suite(self.robot_suite, parent=None)

        modelbased_suite = self.suite_processor(master_suite)
        self.__clearTestSuite(self.robot_suite)
        self.__generateRobotSuite(modelbased_suite, self.robot_suite)

    @keyword(name="Set Model preconditions")
    def set_model_preconditions(self, *args):
        """
        Model precondition can not contain assignments or new objects. It can only contain checks.
        
        Example: Checking that there are no names on the birthday card yet
            Set Model precondition | len(birthday_card.names) \=\= 0
        """
        self._set_model_info('IN', *args)
        for expression in args:
            if ModelSpace.is_new_vocab_expression(expression):
                raise ValueError("Cannot create new vocab terms during precondition checks")
            try:
                eval(expression)
            except SyntaxError:
                raise ValueError("Invalid expression. Note that statements, like assignments, are not valid during precondition checks")
            except:
                pass

    @keyword(name="Set Model postconditions")
    def set_model_postconditions(self, *args):
        """
        Use new <vocab term> to introduce a new domain vocabulaire object. Then assign or update
        properties using python-like expressions.
        
        Example Creating a new birthday_card object with a (still empty) list property for names:
            Set Model postcondition | new birthday_card | birthday_card.names \= []
            
         Note that Robot requires the '=' (equal sign) to be escaped.
        """
        self._set_model_info('OUT', *args)

    def _set_model_info(self, inout, *args):
        for expression in args:
            if not isinstance(expression, str):
                raise TypeError(f"Expression wasn't text but {type(expression)}")
            self.current_step.model_info[inout].append(expression)

    def __process_robot_suite(self, in_suite, parent):
        logger.debug(f"processing test suite: {in_suite.name}")
        out_suite = Suite(in_suite.name, parent)
        out_suite.filename = in_suite.source
        
        if in_suite.setup and parent is not None:
            logger.debug(f"    with setup: {in_suite.setup.name}")
            self.prev_gherkin_kw = None
            step_info = self.__process_step(in_suite.setup, parent=out_suite)
            if step_info.gherkin_kw != 'given':
                step_info.model_info['error'] = "Setup must be a 'given' step"
            out_suite.setup = step_info
        for st in in_suite.suites:
            out_suite.suites.append(self.__process_robot_suite(st, parent=out_suite))
        for tc in in_suite.tests:
            scenario = Scenario(tc.name, parent=out_suite)
            prev_gherkin_kw = None
            logger.debug(f"  test case: {tc.name}")
            if tc.setup:
                logger.debug(f"    with setup: {tc.setup.name}")
                self.prev_gherkin_kw = None
                step_info = self.__process_step(tc.setup, parent=scenario)
                if step_info.gherkin_kw != 'given':
                    step_info.model_info['error'] = "Setup must be a 'given' step"
                scenario.setup = step_info
            logger.debug('    ' + '\n    '.join([st.name + " " + " ".join([str(s) for s in st.args]) for st in tc.body]))
            self.prev_gherkin_kw = None
            for step_def in tc.body:
                step_info = self.__process_step(step_def, parent=scenario)
                scenario.steps.append(step_info)

            out_suite.scenarios.append(scenario)
        return out_suite

    def __process_step(self, step_def, parent):
        step = Step(step_def.name, parent)
        self.prev_gherkin_kw = step.step_kw if str(step.step_kw).lower() in ['given','when','then', 'none'] else self.prev_gherkin_kw
        step.gherkin_kw = step.step_kw if str(step.step_kw).lower() in ['given','when','then'] else self.prev_gherkin_kw
        if step_def.args:
            step.args = step_def.args
        try:
            self.current_step = step
            Robot.run_keyword('model ' + step.bare_kw, *step_def.args)
            self.current_step = None
        except Exception as ex:
            step.model_info['error']=str(ex)
        return step

    def __clearTestSuite(self, suite):
        suite.tests.clear()
        suite.suites.clear()

    def __generateRobotSuite(self, suite_model, target_suite):
        for subsuite in suite_model.suites:
            new_suite = target_suite.suites.create(name=subsuite.name)
            new_suite.resource = target_suite.resource
            if subsuite.setup:
                new_suite.setup = rmodel.Keyword(name=subsuite.setup.keyword, args=subsuite.setup.args, type='setup')
            self.__generateRobotSuite(subsuite, new_suite)
        for tc in suite_model.scenarios:
            new_tc = target_suite.tests.create(name=tc.name)
            if tc.setup:
                new_tc.setup= rmodel.Keyword(name=tc.setup.keyword, args=tc.setup.args, type='setup')
            for step in tc.steps:
                new_tc.body.create_keyword(name=step.keyword, args=step.args)

    def _start_suite(self, suite, result):
        self.current_suite = suite

    def _end_suite(self, suite, result):
        if suite == self.robot_suite:
            self.robot_suite = None
