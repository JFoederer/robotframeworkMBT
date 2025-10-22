from .models import ScenarioGraph, TraceInfo, ScenarioInfo
import networkx as nx
import matplotlib.pyplot as plt
#numpy
#scipy


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide a simple interface through which the graph can be updated, and retrieved in HTML format.
    """
    def __init__(self):
        self.graph = ScenarioGraph()

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_start(self, scenario: ScenarioInfo):
        self.graph.set_starting_node(scenario)

    def set_end(self, scenario: ScenarioInfo):
        self.graph.set_ending_node(scenario)

    def generate_graph(self):
        # temporary code for visualisation  
        self.graph.calculate_pos()
        nx.draw(self.graph.networkx, pos=self.graph.pos, with_labels=True, node_color="lightblue", node_size=600)
        plt.show()

    # TODO: use a graph library to actually create a graph
    def generate_html(self) -> str:
        self.generate_graph()
        return f""
        # return f"<div><p>nodes: {self.graph.nodes}\nedges: {self.graph.edges}\nstart: {self.graph.start}\nend: {self.graph.end}\nids: {[f"{name}: {str(val)}" for (name, val) in self.graph.ids.items()]}</p></div>"
