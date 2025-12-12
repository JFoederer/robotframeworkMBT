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

from .steparguments import StepArguments


class ModellingError(Exception):
    pass


class ModelSpace:
    def __init__(self, reference_id=None):
        self.ref_id = str(reference_id)
        self.std_attrs = []
        self.props = dict()
        self.values = dict()  # For using literals without having to use quotes (abc='abc')
        self.scenario_vars = []
        self.std_attrs = dir(self)

    def __repr__(self):
        return self.ref_id if self.ref_id else super().__repr__()

    def copy(self):
        return copy.deepcopy(self)

    def __eq__(self, other):
        return self.get_status_text() == other.get_status_text()

    def add_prop(self, name):
        if name == 'scenario':
            raise ModellingError(f"scenario is a reserved attribute.")
        if name in self.props or name in self.values:
            raise ModellingError(f"Naming conflict, '{name}' already in use.")
        self.props[name] = ModelSpace(name)
        setattr(self, name, self.props[name])

    def del_prop(self, name):
        if name == 'scenario':
            raise ModellingError(f"scenario is a reserved attribute and cannot be removed.")
        if name not in self.props:
            raise ModellingError(f"Delete failed, '{name}' is not defined.")
        self.props.pop(name)
        delattr(self, name)

    def __dir__(self, recurse=True):
        if recurse:
            return [attr for attr in self.__dir__(False) if attr not in self.std_attrs]
        else:
            return self.__dict__.keys()

    def new_scenario_scope(self):
        self.scenario_vars.append(RecursiveScope(self.scenario_vars[-1] if len(self.scenario_vars) else None))
        self.props['scenario'] = self.scenario_vars[-1]

    def end_scenario_scope(self):
        assert len(self.scenario_vars) > 0, ".end_scenario_scope() called, but there is no scenario scope open."
        self.scenario_vars.pop()
        if len(self.scenario_vars):
            self.props['scenario'] = self.scenario_vars[-1]
        else:
            self.props.pop('scenario')

    def process_expression(self, expression, step_args=StepArguments()):
        expr = step_args.fill_in_args(expression.strip(), as_code=True)
        if self._is_new_vocab_expression(expr):
            self.add_prop(self._vocab_term(expr))
            return 'exec'

        if self._is_del_vocab_expression(expr):
            self.del_prop(self._vocab_term(expr))
            return 'exec'

        local_locals = locals()
        for p in self.props:
            exec(f"{p} = self.props['{p}']", local_locals)
        for v in self.values:
            value = f"'{self.values[v]}'" if isinstance(self.values[v], str) else self.values[v]
            exec(f"{v} = {value}", local_locals)
        try:
            result = eval(expr, local_locals)
        except SyntaxError:
            try:
                exec(expr, local_locals)
                result = 'exec'
            except NameError as missing:
                self.__add_alias(missing.name, step_args)
                result = self.process_expression(expression, step_args)
            except AttributeError as err:
                self.__handle_attribute_error(err)
        except NameError as missing:
            if missing.name == expr:
                raise  # Putting only a name in an expression can be used as exists check
            self.__add_alias(missing.name, step_args)
            result = self.process_expression(expression, step_args)
        except AttributeError as err:
            self.__handle_attribute_error(err)

        for p in self.props:
            exec(f"self.props['{p}'] = {p}", local_locals)

        return result

    def __handle_attribute_error(self, err):
        if isinstance(err.obj, str) and err.obj in self.values:
            # This situation occurs when using e.g. 'foo.bar' in the model before calling 'new foo'.
            # The NameError on foo is handled by adding its alias, which results in an AttributeError
            # 'str' object has no attribute 'bar', but the user wants to know that foo does not exist.
            raise ModellingError(f"{err.obj} used before definition")
        raise ModellingError(f"{err.name} used before assignment")

    def __add_alias(self, missing_name, step_args):
        if missing_name == 'scenario':
            raise ModellingError("Accessing scenario scope while there is no scenario active.\n"
                                 "If you intended this to be a literal, please use quotes ('scenario' or \"scenario\").")
        matching_args = [arg.value for arg in step_args if arg.codestring == missing_name]
        value = matching_args[0] if matching_args else missing_name
        if isinstance(value, str):
            for esc_char in "$@&=":  # Prevent "Syntaxwarning: invalid escape sequence" on Robot escapes like '\$' and '\='
                value = value.replace(f'\\{esc_char}', f'\\\\{esc_char}')
            value = value.replace("'", r"\'")  # Needed because we use single quotes in low level processing later on
        self.values[missing_name] = value

    @staticmethod
    def _is_new_vocab_expression(expression):
        return expression.lower().startswith('new ') and len(expression.split()) == 2

    @staticmethod
    def _is_del_vocab_expression(expression):
        return expression.lower().startswith('del ') and len(expression.split()) == 2

    @staticmethod
    def _vocab_term(expression):
        return expression.split()[-1]

    def get_status_text(self):
        status = str()
        scenario_attrs = []
        for p in self.props:
            if p == 'scenario':
                scenario_attrs = self.props['scenario']
                continue
            status += f"{p}:\n"
            for attr in dir(self.props[p]):
                status += f"    {attr}={getattr(self.props[p], attr)}\n"
        if scenario_attrs:
            status += "scenario:\n"
            for attr, value in scenario_attrs:
                status += f"    {attr}={value}\n"
        return status


class RecursiveScope:
    """
    Generic scoping object with the properties needed for handling scenario variables with refinement.

    In case of refinement the outer scenario can already have set some constraints on the model data.
    This information needs to be available to the inner scenarios as well, as it may need to build
    further upon this data. Further refining the data implies that it also needs to be able to modify
    the already available data to, for instance, add more contraints.

    The resulting behavior is that any action (read or write) on an existing attribute, will be
    executed on the highest available level. Creating new attributes, will make the current level the
    highest available level for that atrribute.
    """

    def __init__(self, outer):
        super().__setattr__('_outer_scope', outer)

    def __getattr__(self, attr):
        if hasattr(super().__getattribute__('_outer_scope'), attr):
            return getattr(self._outer_scope, attr)
        return super().__getattribute__(attr)

    def __setattr__(self, attr, value):
        if hasattr(self._outer_scope, attr):
            setattr(self._outer_scope, attr, value)
        else:
            super().__setattr__(attr, value)

    def __iter__(self):
        return iter([(attr, getattr(self, attr)) for attr in dir(self._outer_scope) + dir(self)
                     if not attr.startswith('__') and attr != '_outer_scope'])

    def __bool__(self):
        return any(True for _ in self)
