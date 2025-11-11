# -*- coding: utf-8 -*-
from .suitedata import Suite, Scenario, Step
from .suiteprocessors import SuiteProcessors
import robot.running.model as rmodel
from robot.api import logger
from robot.api.deco import keyword

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

from robot.libraries.BuiltIn import BuiltIn

Robot = BuiltIn()


class SuiteReplacer:
    ROBOT_LIBRARY_SCOPE: str = 'GLOBAL'
    ROBOT_LISTENER_API_VERSION: int = 3

    def __init__(self, processor: str = 'process_test_suite', processor_lib: str | None = None):
        self.ROBOT_LIBRARY_LISTENER = self  # : Self
        self.current_suite: Suite | None = None
        self.robot_suite: Suite | None = None
        self.processor_lib_name: str | None = processor_lib
        self.processor_name: str = processor
        self._processor_lib: SuiteProcessors | None = None
        self._processor_method = None
        self.processor_options = {}

    @property
    def processor_lib(self) -> SuiteProcessors:
        if self._processor_lib is None:
            self._processor_lib = SuiteProcessors() if self.processor_lib_name is None \
                else Robot.get_library_instance(self.processor_lib_name)
        return self._processor_lib

    @property
    def processor_method(self):
        if self._processor_method is None:
            if not hasattr(self.processor_lib, self.processor_name):
                Robot.fail(
                    f"Processor '{self.processor_name}' not available for model-based processor library {self.processor_lib_name}")

            self._processor_method = getattr(
                self._processor_lib, self.processor_name)

        return self._processor_method

    @keyword(name="Treat this test suite Model-based")
    def treat_model_based(self, **kwargs):
        """
        Add this keyword to a suite setup to treat that test suite model-based.

        In a model-based test suite the test cases are used as building blocks for generating new
        test traces each run, rather than just following the traditional linear path. Based on the
        model info that is included in the test steps, the test cases are modifed, mixed and
        matched to create unique traces and achieve more test coverage quicker.

        Any arguments are handled as if using keyword `Update model-based options`
        """
        self.robot_suite = self.current_suite

        logger.info(
            f"Analysing Robot test suite '{self.robot_suite.name}' for model-based execution.")

        self.update_model_based_options(**kwargs)
        master_suite = self.__process_robot_suite(
            self.robot_suite, parent=None)

        modelbased_suite = self.processor_method(
            master_suite, **self.processor_options)

        self.__clearTestSuite(self.robot_suite)
        self.__generateRobotSuite(modelbased_suite, self.robot_suite)

        # TODO: add flag using kwargs to disable this
        if isinstance(self.processor_lib, SuiteProcessors):
            logger.write(
                self.processor_lib.visualiser.generate_visualisation(), html=True)

    @keyword("Set model-based options")
    def set_model_based_options(self, **kwargs):
        """
        Use one or more named arguments to set any options as listed for the selected
        model-based processor. Removes all previously set options.
        """
        self.processor_options = kwargs

    @keyword("Update model-based options")
    def update_model_based_options(self, **kwargs):
        """
        Use one or more named arguments to set or update any options as listed for the selected
        model-based processor. Keeps any previously set options.
        """
        self.processor_options.update(kwargs)

    def __process_robot_suite(self, in_suite: Suite, parent: Suite | None) -> Suite:
        out_suite = Suite(in_suite.name, parent)
        out_suite.filename = in_suite.source

        if in_suite.setup and parent is not None:
            step_info = Step(in_suite.setup.name, *
                             in_suite.setup.args, parent=out_suite)
            step_info.add_robot_dependent_data(
                Robot._namespace.get_runner(step_info.org_step).keyword)
            out_suite.setup = step_info

        if in_suite.teardown and parent is not None:
            step_info = Step(in_suite.teardown.name, *
                             in_suite.teardown.args, parent=out_suite)
            step_info.add_robot_dependent_data(
                Robot._namespace.get_runner(step_info.org_step).keyword)
            out_suite.teardown = step_info

        for st in in_suite.suites:
            out_suite.suites.append(
                self.__process_robot_suite(st, parent=out_suite))

        for tc in in_suite.tests:
            scenario = Scenario(tc.name, parent=out_suite)
            if tc.setup:
                step_info = Step(
                    tc.setup.name, *tc.setup.args, parent=scenario)
                step_info.add_robot_dependent_data(
                    Robot._namespace.get_runner(step_info.org_step).keyword)
                scenario.setup = step_info

            if tc.teardown:
                step_info = Step(tc.teardown.name, *
                                 tc.teardown.args, parent=scenario)
                step_info.add_robot_dependent_data(
                    Robot._namespace.get_runner(step_info.org_step).keyword)
                scenario.teardown = step_info
            last_gwt = None

            for step_def in tc.body:
                if isinstance(step_def, rmodel.Keyword):
                    step_info = Step(step_def.name, *step_def.args, parent=scenario, assign=step_def.assign,
                                     prev_gherkin_kw=last_gwt)
                    step_info.add_robot_dependent_data(
                        Robot._namespace.get_runner(step_info.org_step).keyword)
                    scenario.steps.append(step_info)

                    if step_info.gherkin_kw:
                        last_gwt = step_info.gherkin_kw

                elif isinstance(step_def, rmodel.Var):
                    scenario.steps.append(
                        Step('VAR', step_def.name, *step_def.value, parent=scenario))
                else:
                    unsupported_step = Step(str(step_def), parent=scenario)
                    unsupported_step.model_info['error'] = f"Robot construct not supported"
                    scenario.steps.append(unsupported_step)

            out_suite.scenarios.append(scenario)

        return out_suite

    def __clearTestSuite(self, suite: Suite):
        suite.tests.clear()
        suite.suites.clear()

    def __generateRobotSuite(self, suite_model: Suite, target_suite):
        for subsuite in suite_model.suites:
            new_suite = target_suite.suites.create(name=subsuite.name)
            new_suite.resource = target_suite.resource
            if subsuite.setup:
                new_suite.setup = rmodel.Keyword(name=subsuite.setup.keyword,
                                                 args=subsuite.setup.posnom_args_str,
                                                 type='setup')
            if subsuite.teardown:
                new_suite.teardown = rmodel.Keyword(name=subsuite.teardown.keyword,
                                                    args=subsuite.teardown.posnom_args_str,
                                                    type='teardown')
            self.__generateRobotSuite(subsuite, new_suite)
        for tc in suite_model.scenarios:
            new_tc = target_suite.tests.create(name=tc.name)
            if tc.setup:
                new_tc.setup = rmodel.Keyword(name=tc.setup.keyword,
                                              args=tc.setup.posnom_args_str,
                                              type='setup')
            if tc.teardown:
                new_tc.teardown = rmodel.Keyword(name=tc.teardown.keyword,
                                                 args=tc.teardown.posnom_args_str,
                                                 type='teardown')
            for step in tc.steps:
                if step.keyword == 'VAR':
                    new_tc.body.create_var(
                        step.posnom_args_str[0], step.posnom_args_str[1:])
                else:
                    new_tc.body.create_keyword(
                        name=step.keyword, assign=step.assign, args=step.posnom_args_str)

    def _start_suite(self, suite: Suite | None, result):
        self.current_suite = suite

    def _end_suite(self, suite: Suite | None, result):
        if suite == self.robot_suite:
            self.robot_suite = None
