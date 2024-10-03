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
        self.values = dict() # For using literals without having to use quotes (abc='abc')
        self.std_attrs = dir(self)

    def __repr__(self):
        return self.ref_id if self.ref_id else super().__repr__()

    def copy(self):
        return copy.deepcopy(self)

    def __eq__(self, other):
        return self.get_status_text() == other.get_status_text()

    def add_prop(self, name):
        if name in self.props or name in self.values:
            raise ModellingError(f"Naming conflict, '{name}' already in use.")
        self.props[name] = ModelSpace(name)
        setattr(self, name, self.props[name])

    def del_prop(self, name):
        if name not in self.props:
            raise ModellingError(f"Delete failed, '{name}' is not defined.")
        self.props.pop(name)
        delattr(self, name)

    def __dir__(self, recurse=True):
        if recurse:
            return [attr for attr in self.__dir__(False) if attr not in self.std_attrs]
        else:
            return self.__dict__.keys()

    def process_expression(self, expression, emb_args=StepArguments()):
        expr = emb_args.fill_in_args(expression.strip(), as_code=True)
        if self._is_new_vocab_expression(expr):
            self.add_prop(self._vocab_term(expr))
            return 'exec'

        if self._is_del_vocab_expression(expr):
            self.del_prop(self._vocab_term(expr))
            return 'exec'

        for p in self.props:
            exec(f"{p} = self.props['{p}']")
        for v in self.values:
            exec(f"{v} = '{self.values[v]}'")
        try:
            result = eval(expr, locals())
        except SyntaxError:
            try:
                exec(expr, locals())
                result = 'exec'
            except NameError as missing:
                self.__add_alias(missing.name, emb_args)
                result = self.process_expression(expression, emb_args)
            except AttributeError as err:
                raise ModellingError(f"{err.name} used before assignment")
        except NameError as missing:
            if missing.name == expr:
                raise # Putting only a name in an expression can be used as exists check
            self.__add_alias(missing.name, emb_args)
            result = self.process_expression(expression, emb_args)
        except AttributeError as err:
            raise ModellingError(f"{err.name} used before assignment")

        for p in self.props:
            exec(f"self.props['{p}'] = {p}")

        return result

    def __add_alias(self, missing_name, emb_args):
        matching_args = [arg.value for arg in emb_args if arg.codestring == missing_name]
        self.values[missing_name] = matching_args[0].replace("'", r"\'") if matching_args else missing_name

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
        for p in self.props:
            status += f"{p}:\n"
            for attr in dir(self.props[p]):
                status += f"    {attr}={getattr(self.props[p], attr)}\n"
        return status
