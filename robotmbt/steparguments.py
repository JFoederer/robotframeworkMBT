# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2024, J. Foederer
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

from keyword import iskeyword
import builtins


class StepArguments(list):
    def __init__(self, iterable=[]):
        super().__init__(item.copy() for item in iterable)

    def fill_in_args(self, text: str, as_code: bool = False) -> str:
        result = text
        for arg in self:
            sub = arg.codestring if as_code else str(arg.value)
            result = result.replace(arg.arg, sub)
        return result

    def __getitem__(self, key):
        for steparg in self:
            if key.casefold() == steparg.arg.casefold():
                return steparg
        return super()[key]

    @property
    def modified(self) -> bool:
        return any([arg.modified for arg in self])


class StepArgument:
    EMBEDDED = 'EMBEDDED'
    POSITIONAL = 'POSITIONAL'
    VAR_POS = 'VAR_POS'
    NAMED = 'NAMED'
    FREE_NAMED = 'FREE_NAMED'

    def __init__(self, arg_name: str, value: any, kind: str | None = None):
        self.name: str = arg_name
        self.org_value: any = value
        self.kind: str | None = kind
        self._value: any = None
        self._codestr: str | None = None
        self.value: any = value

    @property
    def arg(self) -> str:
        return "${%s}" % self.name

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, value: any):
        self._value = value
        self._codestr = self.make_codestring(value)

    @property
    def modified(self) -> bool:
        return self.org_value != self.value

    @property
    def codestring(self) -> str | None:
        return self._codestr

    def copy(self):
        # -> Self
        cp = StepArgument(self.arg.strip('${}'), self.value, self.kind)
        cp.org_value = self.org_value
        return cp

    @staticmethod
    def make_codestring(text: any) -> str:
        codestr = str(text)
        if codestr.title() in ['None', 'True', 'False']:
            return codestr.title()
        try:
            float(codestr)
        except:
            codestr = StepArgument.make_identifier(codestr)
        return codestr

    @staticmethod
    def make_identifier(s: any) -> str:
        _s = str(s).replace(' ', '_')
        if _s.isidentifier():
            return f"{_s}_" if iskeyword(_s) or _s in dir(builtins) else _s
        if _s[:1].isdecimal():
            _s = f'_{_s}'
        return ''.join([c if c.isidentifier() or c.isdecimal() else f"o{ord(c)}" for c in _s])
