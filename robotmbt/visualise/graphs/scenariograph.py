# BSD 3-Clause License
#
# Copyright (c) 2026, T.B. Dubbeling,  J. Foederer, T.S. Kas, D.R. Osinga, D.F. Serra e Silva, J.C. Willegers
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

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo


class ScenarioGraph(AbstractGraph[ScenarioInfo, None]):
    """
    The scenario graph is the most basic representation of trace exploration.
    It represents scenarios as nodes, and the trace as edges.
    """

    @staticmethod
    def select_node_info(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> ScenarioInfo:
        return trace[index][0]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_description(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> str:
        return ''

    @staticmethod
    def create_node_label(info: ScenarioInfo) -> str:
        return info.name

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Executed Scenario (in final trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Executed Scenario (backtracked)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "Execution Flow (final trace)"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "Execution Flow (backtracked)"

    @staticmethod
    def get_tooltip_name() -> str:
        return ""
