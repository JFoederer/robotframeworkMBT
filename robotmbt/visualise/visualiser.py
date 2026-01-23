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

GRAPHS = {
    'scenario': ScenarioGraph,
    'state': StateGraph,
    'scenario-state': ScenarioStateGraph,
    'delta-value': DeltaValueGraph,
    'scenario-delta-value': ScenarioDeltaValueGraph,
    'reduced-sdv': ReducedSDVGraph,
}


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

    def __init__(self, graph_type: str, suite_name: str = "", export: str = '', trace_info: TraceInfo = None):
        if not export and not graph_type in GRAPHS.keys():
            raise ValueError(f"Unknown graph type: {graph_type}")

        self.graph_type: str = graph_type

        if trace_info is None:
            self.trace_info: TraceInfo = TraceInfo()
        else:
            self.trace_info = trace_info

        self.suite_name = suite_name
        self.export = export

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

    def _get_graph(self) -> AbstractGraph | None:
        if self.graph_type not in GRAPHS.keys():
            return None

        return GRAPHS[self.graph_type](self.trace_info)

    def generate_visualisation(self) -> tuple[str, bool]:
        """
        Finalize the visualisation. Exports the graph to JSON if requested, and generates HTML if requested.
        The boolean signals whether the output is in HTML format or not.
        """
        if self.export:
            self.trace_info.export_graph(self.suite_name, self.export)

        graph: AbstractGraph = self._get_graph()
        if graph is None and self.export:
            return f"Successfully exported to {self.export}!", False
        elif graph is None:
            raise ValueError(f"Unknown graph type: {self.graph_type}")

        html_bokeh = networkvisualiser.NetworkVisualiser(graph, self.suite_name).generate_html()

        return f'<iframe srcdoc="{html.escape(html_bokeh)}" width="{networkvisualiser.OUTER_WINDOW_WIDTH}px" height="{networkvisualiser.OUTER_WINDOW_HEIGHT}px"></iframe>', True
