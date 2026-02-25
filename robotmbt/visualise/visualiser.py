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

from robotmbt.modelspace import ModelSpace
from robotmbt.tracestate import TraceState
from robotmbt.visualise import networkvisualiser
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
from robotmbt.visualise.models import TraceInfo, StateInfo, ScenarioInfo
import html

GRAPHS = {
    'scenario': ScenarioGraph,
    'scenario-delta-value': ScenarioDeltaValueGraph,
}


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide
    a simple interface through which the graph can be updated,
    and retrieved in HTML format.
    """

    def __init__(self, suite_name: str = "", trace_info: TraceInfo = None):
        self.trace_info: TraceInfo = trace_info if trace_info is not None else TraceInfo(suite_name)
        self.suite_name = suite_name

    def load_from_file(self, file_path: str):
        """
        Imports a JSON encoding of a graph and reconstructs the graph from it. The reconstructed
        graph overrides the current graph instance this method is called on.
        file_path: the path to a previously exported graph.
        """
        self.trace_info = TraceInfo.import_graph_from_file(file_path)

    def export_to_file(self, file_path: str):
        self.trace_info.export_graph(file_path)

    def update_trace(self, trace: TraceState):
        """
        Uses the new snapshots from trace to update the trace info.
        Multiple new snapshots can be pushed or popped at once.
        """
        trace_len = len(trace._snapshots)
        # We don't have any information
        if trace_len == 0:
            self.trace_info.update_trace(None, StateInfo(ModelSpace()), 0)

        # New snapshots have been pushed
        elif trace_len > self.trace_info.previous_length:
            prev = self.trace_info.previous_length
            r = trace_len - prev
            # Extract all snapshots that have been pushed and update our trace info with their scenario/model info
            for i in range(r):
                snap = trace._snapshots[prev + i]
                scenario = snap.scenario
                model = snap.model
                self.trace_info.update_trace(ScenarioInfo(scenario), StateInfo(model), prev + i + 1)

        # Snapshots have been removed
        else:
            snap = trace._snapshots[-1]
            scenario = snap.scenario
            model = snap.model
            self.trace_info.update_trace(ScenarioInfo(scenario), StateInfo(model), trace_len)

    def _get_graph(self, graph_type) -> AbstractGraph | None:
        if graph_type not in GRAPHS.keys():
            return None

        return GRAPHS[graph_type](self.trace_info)

    def generate_visualisation(self, graph_type: str) -> str:
        """
        Finalize the visualisation. Exports the graph to JSON if requested, and generates HTML if requested.
        The boolean signals whether the output is in HTML format or not.
        """
        graph: AbstractGraph = self._get_graph(graph_type)
        if graph is None:
            raise ValueError(f"Unknown graph type: {graph_type}")

        html_bokeh = networkvisualiser.NetworkVisualiser(graph, self.trace_info.model_name).generate_html()
        return f'<iframe srcdoc="{html.escape(html_bokeh)}" width="{networkvisualiser.OUTER_WINDOW_WIDTH}px" height="{networkvisualiser.OUTER_WINDOW_HEIGHT}px"></iframe>'
