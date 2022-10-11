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

import re

from robot.libraries.BuiltIn import BuiltIn;Robot = BuiltIn()
from robot.api.deco import keyword
from robot.api import logger
import robot.running.model as rmodel
from robot.running.arguments import EmbeddedArguments

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
                                            else Robot.get_library_instance(processor_lib)
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

    def __process_robot_suite(self, in_suite, parent):
        logger.debug(f"processing test suite: {in_suite.name}")
        out_suite = Suite(in_suite.name, parent)
        out_suite.filename = in_suite.source
        
        if in_suite.setup and parent is not None:
            logger.debug(f"    with setup: {in_suite.setup.name}")
            self.prev_gherkin_kw = None
            step_info = self.__process_step(in_suite.setup, parent=out_suite)
            out_suite.setup = step_info
        if in_suite.teardown and parent is not None:
            logger.debug(f"    with teardown: {in_suite.teardown.name}")
            self.prev_gherkin_kw = None
            step_info = self.__process_step(in_suite.teardown, parent=out_suite)
            out_suite.teardown = step_info
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
                scenario.setup = step_info
            if tc.teardown:
                logger.debug(f"    with teardown: {tc.teardown.name}")
                self.prev_gherkin_kw = None
                step_info = self.__process_step(tc.teardown, parent=scenario)
                scenario.teardown = step_info
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
            try:
                step.model_info = self.__parse_model_info(step)
            except ValueError as err:
                step.model_info = dict(error=str(err))
            self.current_step = None
        except Exception as ex:
            step.model_info['error']=str(ex)
        return step

    def __parse_model_info(self, step):
        model_info = dict()
        docu = Robot._namespace.get_runner(step.bare_kw)._handler.doc
        mi_index = docu.find("*model info*")
        if mi_index == -1:
            return model_info
        lines = docu[mi_index:].split('\n')
        lines = [line.strip() for line in lines][1:]
        if "" in lines:
            lines = lines[:lines.index("")]
        format_msg = "*model info* expected format: :<attr>: <expr>|<expr>"
        while lines:
            line = lines.pop(0)
            if not line.startswith(":"):
                raise ValueError(format_msg)
            elms = line.split(":", 2)
            if len(elms) != 3:
                raise ValueError(format_msg)
            key = elms[1].strip()
            values = [e.strip() for e in elms[-1].split("|") if e]
            while lines and not lines[0].startswith(":"):
                values.extend([e.strip() for e in lines.pop(0).split("|") if e])
            values = self.__fill_in_args(step, values)
            model_info[key] = values
        if not model_info:
            raise ValueError("When present, *model info* cannot be empty")
        return model_info

    def __fill_in_args(self, step, expressions):
        kw_def = Robot._namespace.get_runner(step.bare_kw)._handler.name
        emb_args = EmbeddedArguments.from_name(kw_def)
        re_pattern = emb_args.name
        arg_values = dict()
        if re_pattern:
            arg_values = dict(zip(["${%s}"%a for a in emb_args.args],
                                  re.match(re_pattern, step.bare_kw).groups()))
        result = []
        for expr in expressions:
            result.append(expr)
            for arg, value in arg_values.items():
                result[-1] = result[-1].replace(arg, value)
        return result

    def __clearTestSuite(self, suite):
        suite.tests.clear()
        suite.suites.clear()

    def __generateRobotSuite(self, suite_model, target_suite):
        for subsuite in suite_model.suites:
            new_suite = target_suite.suites.create(name=subsuite.name)
            new_suite.resource = target_suite.resource
            if subsuite.setup:
                new_suite.setup = rmodel.Keyword(name=subsuite.setup.keyword,
                                                 args=subsuite.setup.args,
                                                 type='setup')
            if subsuite.teardown:
                new_suite.teardown = rmodel.Keyword(name=subsuite.teardown.keyword,
                                                    args=subsuite.teardown.args,
                                                    type='teardown')
            self.__generateRobotSuite(subsuite, new_suite)
        for tc in suite_model.scenarios:
            new_tc = target_suite.tests.create(name=tc.name)
            if tc.setup:
                new_tc.setup= rmodel.Keyword(name=tc.setup.keyword,
                                             args=tc.setup.args,
                                             type='setup')
            if tc.teardown:
                new_tc.teardown= rmodel.Keyword(name=tc.teardown.keyword,
                                                args=tc.teardown.args,
                                                type='teardown')
            for step in tc.steps:
                new_tc.body.create_keyword(name=step.keyword, args=step.args)

    def _start_suite(self, suite, result):
        self.current_suite = suite

    def _end_suite(self, suite, result):
        if suite == self.robot_suite:
            self.robot_suite = None
