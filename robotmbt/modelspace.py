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

class ModellingError(Exception):
    pass

class ModelSpace:
    def __init__(self, ):
        self.std_attrs = []
        self.props = dict()
        self.values = []
        self.std_attrs = dir(self)

    def add_prop(self, name):
        if name in self.props or name in self.values:
            raise ModellingError(f"Naming conflict, '{name}' already in use.")
        self.props[name] = ModelSpace()
        setattr(self, name, self.props[name])

    def __dir__(self, recurse=True):
        if recurse:
            return [attr for attr in self.__dir__(False) if attr not in self.std_attrs]
        else:
            return self.__dict__.keys()

    def process_expression(self, expr):
        if self.is_new_vocab_expression(expr):
            self.add_prop(self.new_vocab_term(expr))
            return 'exec'

        for p, obj in self.props.items():
            action = f"{p} = self.props['{p}']"
            exec(action)
        for v in self.values:
            action = f"{v} = '{v}'"
            exec(action)
        try:
            result = eval(expr)
        except SyntaxError:
            try:
                exec(expr)
            except NameError as missing:
                self.values.append(missing.name)
                self.process_expression(expr)
            result = 'exec'

        proplist = self.props.keys()
        for p in self.props:
            action = f"self.props['{p}'] = {p}"
            exec(action)

        return result

    @staticmethod
    def is_new_vocab_expression(expression):
        return expression.lower().startswith('new ') and len(expression.split()) == 2

    @staticmethod
    def new_vocab_term(expression):
        return expression.split()[-1]

    def get_status_text(self):
        status = str()
        for p, v in self.props.items():
            status += f"{p}:\n"
            for attr in dir(self.props[p]):
                status += f"    {attr}={getattr(self.props[p], attr)}\n"
        return status
