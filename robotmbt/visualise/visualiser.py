from robotmbt.modelspace import ModelSpace
from robotmbt.tracestate import TraceState
from robotmbt.visualise import networkvisualiser
from robotmbt.visualise.graphs.deltavaluegraph import DeltaValueGraph
from robotmbt.visualise.graphs.reducedSDVgraph import ReducedSDVGraph
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
from robotmbt.visualise.graphs.stategraph import StateGraph
from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
from robotmbt.visualise.models import TraceInfo, StateInfo, ScenarioInfo
import html


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide
    a simple interface through which the graph can be updated,
    and retrieved in HTML format.
    """

    # glue method to let us construct Visualiser objects in Robot tests.
    @classmethod
    def construct(cls, graph_type: str):
        # just calls __init__, but without having underscores etc.
        return cls(graph_type)

    def __init__(self, graph_type: str, suite_name: str = "", seed: str = "", export: bool = False,
                 trace_info: TraceInfo = None):
        if graph_type != 'scenario' and graph_type != 'state' and graph_type != 'scenario-state' \
                and graph_type != 'scenario-delta-value' and graph_type != 'reduced-sdv' \
                and graph_type != 'delta-value':
            raise ValueError(f"Unknown graph type: {graph_type}!")

        self.graph_type: str = graph_type
        if trace_info == None:
            self.trace_info: TraceInfo = TraceInfo()
        else:
            self.trace_info = trace_info
        self.suite_name = suite_name
        self.export = export
        self.seed = seed

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
                if model is None:
                    model = ModelSpace
                self.trace_info.update_trace(ScenarioInfo(scenario), StateInfo(model), prev + i + 1)

        # Snapshots have been removed
        else:
            snap = trace._snapshots[-1]
            scenario = snap.scenario
            model = snap.model
            self.trace_info.update_trace(ScenarioInfo(scenario), StateInfo(model), trace_len)

    def generate_visualisation(self) -> str:
        if self.export:
            self.trace_info.export_graph(self.suite_name)

        if self.graph_type == 'scenario':
            graph: AbstractGraph = ScenarioGraph(self.trace_info)
        elif self.graph_type == 'state':
            graph: AbstractGraph = StateGraph(self.trace_info)
        elif self.graph_type == 'scenario-delta-value':
            graph: AbstractGraph = ScenarioDeltaValueGraph(self.trace_info)
        elif self.graph_type == 'reduced-sdv':
            graph: AbstractGraph = ReducedSDVGraph(self.trace_info)
        elif self.graph_type == 'delta-value':
            graph: AbstractGraph = DeltaValueGraph(self.trace_info)
        else:
            graph: AbstractGraph = ScenarioStateGraph(self.trace_info)

        html_bokeh = networkvisualiser.NetworkVisualiser(graph, self.suite_name, self.seed).generate_html()

        return f'<iframe srcdoc="{html.escape(html_bokeh)}" width="{networkvisualiser.OUTER_WINDOW_WIDTH}px" height="{networkvisualiser.OUTER_WINDOW_HEIGHT}px"></iframe>'
