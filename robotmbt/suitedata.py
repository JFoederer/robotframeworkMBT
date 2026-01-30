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

import copy
from typing import Literal

from robot.errors import ExecutionFailed  # Raised by Robot in case of keyword timeout
from robot.running.arguments.argumentspec import ArgumentSpec
from robot.running.arguments.argumentvalidator import ArgumentValidator
from robot.running.keywordimplementation import KeywordImplementation
import robot.utils.notset

from .steparguments import StepArgument, StepArguments, ArgKind
from .substitutionmap import SubstitutionMap


class Suite:
    def __init__(self, name: str, parent=None):
        self.name: str = name
        self.filename: str = ''
        self.parent: Suite | None = parent
        self.suites: list[Suite] = []
        self.scenarios: list[Scenario] = []
        self.setup: Step | None = None  # Can be a single step or None
        self.teardown: Step | None = None  # Can be a single step or None

    @property
    def longname(self) -> str:
        return f"{self.parent.longname}.{self.name}" if self.parent else self.name

    def has_error(self) -> bool:
        return ((self.setup.has_error() if self.setup else False)
                or any([s.has_error() for s in self.suites])
                or any([s.has_error() for s in self.scenarios])
                or (self.teardown.has_error() if self.teardown else False))

    def steps_with_errors(self):
        return (([self.setup] if self.setup and self.setup.has_error() else [])
                + [e for s in map(Suite.steps_with_errors, self.suites) for e in s]
                + [e for s in map(Scenario.steps_with_errors, self.scenarios) for e in s]
                + ([self.teardown] if self.teardown and self.teardown.has_error() else []))


class Scenario:
    def __init__(self, name: str, parent: Suite | None = None):
        self.name: str = name
        # Parent scenario is kept for easy searching, processing and referencing
        # after steps and scenarios have been potentially moved around
        self.parent: Suite | None = parent
        self.setup: Step | None = None  # Can be a single step or None
        self.teardown: Step | None = None  # Can be a single step or None
        self.steps: list[Step] = []
        self.src_id: int | None = None
        self.data_choices: SubstitutionMap = SubstitutionMap()

    @property
    def longname(self) -> str:
        return f"{self.parent.longname}.{self.name}" if self.parent else self.name

    def has_error(self) -> bool:
        return ((self.setup.has_error() if self.setup else False)
                or any([s.has_error() for s in self.steps])
                or (self.teardown.has_error() if self.teardown else False))

    def steps_with_errors(self):
        return (([self.setup] if self.setup and self.setup.has_error() else [])
                + [s for s in self.steps if s.has_error()]
                + ([self.teardown] if self.teardown and self.teardown.has_error() else []))

    def copy(self):
        duplicate = copy.copy(self)
        duplicate.steps = [step.copy() for step in self.steps]
        duplicate.data_choices = self.data_choices.copy()
        return duplicate

    def split_at_step(self, stepindex: int):
        """Returns 2 partial scenarios.

        With stepindex 0 the first part has no steps and all steps are in the last part. With
        stepindex 1 the first step is in the first part, the other in the last part, and so on.
        """
        assert stepindex <= len(self.steps), "Split index out of range. Not enough steps in scenario."
        front = self.copy()
        front.teardown = None
        front.steps = self.steps[:stepindex]
        back = self.copy()
        back.steps = self.steps[stepindex:]
        back.setup = None
        return front, back


class Step:
    def __init__(self, steptext: str, *args, parent: Suite | Scenario, assign: tuple[str] = (),
                 prev_gherkin_kw: Literal['given', 'when', 'then'] | None = None):
        # org_step is the first keyword cell of the Robot line, including step_kw,
        # excluding positional args, excluding variable assignment.
        self.org_step: str = steptext
        # org_pn_args are the positional and named arguments as parsed
        # from the Robot text ('posA' , 'posB', 'named1=namedA')
        self.org_pn_args: tuple[str, ...] = args
        self.parent: Suite | Scenario = parent  # Parent scenario for easy searching and processing.
        # For when a keyword's return value is assigned to a variable.
        # Taken directly from Robot.
        self.assign: tuple[str] = assign
        # gherkin_kw is one of 'given', 'when', 'then', or None for non-bdd keywords.
        self.gherkin_kw = self.step_kw if \
            str(self.step_kw).lower() in ['given', 'when', 'then', 'none'] else prev_gherkin_kw
        self.signature: str | None = None  # Robot keyword with its embedded arguments in ${...} notation.
        self.args: StepArguments = StepArguments()  # embedded arguments list of StepArgument objects.
        self.detached: bool = False  # Decouples StepArguments from the step text (refinement use case)
        # model_info contains modelling information as a dictionary. The standard format is
        # dict(IN=[], OUT=[]) and can optionally contain an error field.
        # The values of IN and OUT are lists of Python evaluatable expressions.
        # The `new vocab` form can be used to create new domain objects.
        # The `vocab.attribute` form can then be used to express relations
        # between properties from the domain vocabulaire.
        # Custom processors can define their own attributes.
        self.model_info: dict[str, str | list[str]] = dict()

    def __str__(self):
        return self.keyword

    def __repr__(self):
        return f"Step: '{self}' with model info: {self.model_info}"

    def copy(self):
        cp = Step(self.org_step, *self.org_pn_args, parent=self.parent, assign=self.assign)
        cp.gherkin_kw = self.gherkin_kw
        cp.signature = self.signature
        cp.args = StepArguments(self.args)
        cp.detached = self.detached
        cp.model_info = self.model_info.copy()
        return cp

    def has_error(self) -> bool:
        return 'error' in self.model_info

    def get_error(self) -> str | None:
        return self.model_info.get('error')

    @property
    def full_keyword(self) -> str:
        """The full keyword text, quad space separated, including its arguments and return value assignment"""
        return "    ".join(str(p) for p in (*self.assign, self.keyword, *self.posnom_args_str))

    @property
    def keyword(self) -> str:
        if not self.signature:
            return self.org_step
        s = f"{self.step_kw} {self.signature}" if self.step_kw else self.signature
        return self.args.fill_in_args(s)

    @property
    def posnom_args_str(self) -> tuple[str, ...]:
        """A tuple with all arguments in Robot accepted text format ('posA' , 'posB', 'named1=namedA')"""
        if self.detached or not self.args.modified:
            return self.org_pn_args
        result = []
        for arg in self.args:
            if arg.is_default:
                continue
            if arg.kind == ArgKind.POSITIONAL:
                result.append(arg.value)
            elif arg.kind == ArgKind.VAR_POS:
                for vararg in arg.value:
                    result.append(vararg)
            elif arg.kind == ArgKind.NAMED:
                result.append(f"{arg.name}={arg.value}")
            elif arg.kind == ArgKind.FREE_NAMED:
                for name, value in arg.value.items():
                    result.append(f"{name}={value}")
            else:
                continue
        return tuple(result)

    @property
    def gherkin_kw(self) -> Literal['given', 'when', 'then'] | None:
        return self._gherkin_kw

    @gherkin_kw.setter
    def gherkin_kw(self, value: str | None):
        """if value is type str, it must be a case insensitive variant of given, when, then"""
        self._gherkin_kw = value.lower() if value else None

    @property
    def step_kw(self) -> str | None:
        first_word = self.org_step.split()[0]
        return first_word if first_word.lower() in ['given', 'when', 'then', 'and', 'but'] else None

    @property
    def kw_wo_gherkin(self) -> str:
        """The keyword without its Gherkin keyword. I.e., as it is known in Robot framework."""
        return self.keyword.replace(self.step_kw, '', 1).strip() if self.step_kw else self.keyword

    def add_robot_dependent_data(self, robot_kw: KeywordImplementation):
        """robot_kw must be Robot Framework's keyword object from Robot's runner context"""
        try:
            if robot_kw.error:
                raise ValueError(robot_kw.error)
            if robot_kw.embedded:
                self.args = StepArguments([StepArgument(*match, kind=ArgKind.EMBEDDED) for match in
                                           zip(robot_kw.embedded.args,
                                               robot_kw.embedded.parse_args(self.kw_wo_gherkin))])
            self.args += self.__handle_non_embedded_arguments(robot_kw.args)
            self.signature = robot_kw.name
            self.model_info = self.__parse_model_info(robot_kw._doc)
        except ExecutionFailed:
            raise
        except Exception as ex:
            self.model_info['error'] = str(ex)

    def __handle_non_embedded_arguments(self, robot_argspec: ArgumentSpec) -> list[StepArgument]:
        result = []
        p_args = [a for a in self.org_pn_args if '=' not in a or r'\=' in a]
        n_args = [a.split('=', 1) for a in self.org_pn_args if '=' in a and r'\=' not in a]
        self.__validate_arguments(robot_argspec, p_args, n_args)

        robot_args = [a for a in robot_argspec]
        argument_names = [a for a in robot_argspec.argument_names if a not in robot_argspec.embedded]
        for arg in robot_argspec:
            if not p_args or (arg.kind != arg.POSITIONAL_ONLY and arg.kind != arg.POSITIONAL_OR_NAMED):
                break
            result.append(StepArgument(argument_names.pop(0), p_args.pop(0), kind=ArgKind.POSITIONAL))
            robot_args.pop(0)
        if p_args and robot_args[0].kind == robot_args[0].VAR_POSITIONAL:
            result.append(StepArgument(argument_names.pop(0), p_args, kind=ArgKind.VAR_POS))
        free = {}
        for name, value in n_args:
            if name in argument_names:
                result.append(StepArgument(name, value, kind=ArgKind.NAMED))
                argument_names.remove(name)
            else:
                free[name] = value
        if free:
            result.append(StepArgument(argument_names.pop(-1), free, kind=ArgKind.FREE_NAMED))
        for unmentioned_arg in argument_names:
            arg = next(arg for arg in robot_args if arg.name == unmentioned_arg)
            default_value = arg.default
            if default_value is robot.utils.notset.NOT_SET:
                if arg.kind == arg.VAR_POSITIONAL:
                    default_value = []
                elif arg.kind == arg.VAR_NAMED:
                    default_value = {}
                else:
                    # This can happen when using library keywords that specify embedded arguments in the @keyword decorator
                    # but use different names in the method signature. Robot Framework implementation is incomplete for this
                    # aspect and differs between library and user keywords.
                    assert False, f"No default argument expected to be needed for '{unmentioned_arg}' here"
            result.append(StepArgument(unmentioned_arg, default_value, kind=ArgKind.NAMED, is_default=True))
        return result

    @staticmethod
    def __validate_arguments(spec, positionals, nameds):
        # Robot uses a slightly different mapping for positional and named arguments.
        # We keep the notation from the scenario (with or without the argument's name).
        # Robot's mapping favours positional when possible, even when the name is used
        # in the keyword call. The validator is sensitive to these differences.
        p, n = spec.map(positionals, nameds)
        if p == [None]:
            # for some reason .map() returns [None] instead of the empty list when there are no arguments
            p = []
        # Use the Robot mechanism for validation to yield familiar error messages
        ArgumentValidator(spec).validate(p, n)

    def __parse_model_info(self, docu: str) -> dict[str, list[str]]:
        model_info = dict()
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
            expressions = [e.strip() for e in elms[-1].split("|") if e]
            while lines and not lines[0].startswith(":"):
                expressions.extend([e.strip() for e in lines.pop(0).split("|") if e])
            model_info[key] = expressions
        if not model_info:
            raise ValueError("When present, *model info* cannot be empty")
        return model_info
