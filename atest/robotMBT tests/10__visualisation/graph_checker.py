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

import os
from typing import Literal
from robot.api.deco import library, keyword
try:
    from robotmbt.visualise.visualiser import Visualiser
    from robotmbt.visualise.networkvisualiser import NetworkVisualiser
except ImportError:
    Visualiser = None


@library(scope='SUITE', auto_keywords=True)
class GraphChecker:
    def graphing_dependencies_missing(self) -> bool:
        return Visualiser is None

    def clear_prior_exports(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            if os.path.exists(file_path):
                raise OSError(f"Removing previous export file '{file_path}' failed")

    def import_graph_data_from(self, file_path: str, graph_type: str = 'scenario'):
        self.visualiser = Visualiser()
        self.visualiser.load_from_file(file_path)
        self.graph = self.visualiser._get_graph(graph_type)
        self.nxgraph = self.graph.networkx

    @property
    def to_node(self) -> dict[str, str]:
        """scenario name to node id converter"""
        node_dict = {self._label_to_scenario(node['label']): id for id, node in self.nxgraph.nodes().items()}
        if len(node_dict) < self.number_of_graph_nodes():
            print("Warning: Repeated scenario names present in graph")
        return node_dict

    @property
    def from_node(self) -> dict[str, str]:
        """node id to scenario name converter"""
        return {id: self._label_to_scenario(node['label']) for id, node in self.nxgraph.nodes().items()}

    def number_of_graph_nodes(self) -> int:
        return len(self.nxgraph.nodes())

    def list_of_node_titles(self) -> list[str]:
        return list(self.to_node)

    def full_node_text_of_node(self, node_title: str) -> str:
        node = self.to_node[node_title]
        return self.nxgraph.nodes()[node]['label']

    def all_successors_to_node(self, node_title: str) -> list[str]:
        return [self.from_node[node] for node in self.nxgraph.successors(self.to_node[node_title])]

    def vertical_position_of_node(self, node_title: str) -> int:
        nxvisual = NetworkVisualiser(self.graph, 'dummy')
        return nxvisual.node_dict[self.to_node[node_title]].y

    @keyword("Modify export file with future ${bump} version number")
    def modify_export_file_with_future_version_number(self, bump: Literal['major', 'minor'], file_path: str) -> str:
        with open(file_path, "r") as f:
            contents = f.read()
        new_file = file_path.replace('.json', '_future.json')
        new_version = '2.0.0' if bump == 'major' else '1.1.1'
        with open(new_file, "w") as f:
            f.write(contents.replace('"ROBOTMBT_MODEL_VERSION": "1.0.0"', f'"ROBOTMBT_MODEL_VERSION": "{new_version}"'))
        return new_file

    def corrupt_export_file(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            contents = f.read()
        new_file = file_path.replace('.json', '_corrupt.json')
        with open(new_file, "w") as f:
            f.write(contents)
            f.seek(0)
            f.write('corrupted-'*20)
        return new_file

    @staticmethod
    def _label_to_scenario(labeltext: str) -> str:
        return labeltext.split("\n\n")[0].replace('\n', ' ')
