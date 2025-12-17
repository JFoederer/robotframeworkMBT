from robotmbt.modelspace import ModelSpace
from robotmbt.tracestate import TraceState
from robotmbt.visualise.graphs.reducedSDVgraph import ReducedSDVGraph
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise import networkvisualiser
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

    def __init__(self, graph_type: str, suite_name: str = ""):
        if graph_type != 'scenario' and graph_type != 'state' and graph_type != 'scenario-state' \
                and graph_type != 'scenario-delta-value' and graph_type != 'reduced-sdv':
            raise ValueError(f"Unknown graph type: {graph_type}!")

        self.graph_type: str = graph_type
        self.trace_info: TraceInfo = TraceInfo()
        self.suite_name = suite_name

    def update_trace(self, trace: TraceState, state: ModelSpace):
        if len(trace.get_trace()) > 0:
            self.trace_info.update_trace(ScenarioInfo(trace.get_trace()[-1]), StateInfo(state), len(trace.get_trace()))
        else:
            self.trace_info.update_trace(None, StateInfo(state), 0)

    def generate_visualisation(self) -> str:
        if self.graph_type == 'scenario':
            graph: AbstractGraph = ScenarioGraph(self.trace_info)
        elif self.graph_type == 'state':
            graph: AbstractGraph = StateGraph(self.trace_info)
        elif self.graph_type == 'scenario-delta-value':
            graph: AbstractGraph = ScenarioDeltaValueGraph(self.trace_info)
        elif self.graph_type == 'reduced-sdv':
            graph: AbstractGraph = ReducedSDVGraph(self.trace_info)
        else:
            graph: AbstractGraph = ScenarioStateGraph(self.trace_info)
        
        vis = networkvisualiser.NetworkVisualiser(graph, self.suite_name)
        html_bokeh = vis.generate_html()
        
        graph_size = networkvisualiser.NetworkVisualiser.GRAPH_SIZE_PX
        
        return f'<iframe srcdoc="{html.escape(html_bokeh)}" width="{graph_size}px" height="{graph_size}px"></iframe>'