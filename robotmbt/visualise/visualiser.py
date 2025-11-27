from robotmbt.visualise.networkvisualiser import NetworkVisualiser
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
from robotmbt.visualise.graphs.stategraph import StateGraph
from robotmbt.visualise.graphs.scenariostategraph import ScenarioStateGraph
from robotmbt.visualise.models import TraceInfo
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

    def __init__(self, graph_type: str):
        if graph_type == 'scenario':
            self.graph: AbstractGraph = ScenarioGraph()
        elif graph_type == 'state':
            self.graph: AbstractGraph = StateGraph()
        elif graph_type == 'scenario-state':
            self.graph: AbstractGraph = ScenarioStateGraph()
        else:
            raise ValueError(f"Unknown graph type: {graph_type}!")

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_final_trace(self, info: TraceInfo):
        self.graph.set_final_trace(info)

    def generate_visualisation(self) -> str:
        html_bokeh = NetworkVisualiser(self.graph).generate_html()
        return f"<iframe srcdoc=\"{html.escape(html_bokeh)}\", \
            width=\"{NetworkVisualiser.GRAPH_SIZE_PX}px\", \
            height=\"{NetworkVisualiser.GRAPH_SIZE_PX}px\">\
            </iframe>"
