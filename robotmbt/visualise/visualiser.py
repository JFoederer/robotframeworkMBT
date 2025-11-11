from .models import ScenarioGraph, TraceInfo, ScenarioInfo
from bokeh.palettes import Spectral4
from bokeh.models import (
    Plot, Range1d, Circle, Rect,
    Arrow, NormalHead, LabelSet,
    Bezier, ColumnDataSource, ResetTool,
    SaveTool, WheelZoomTool, PanTool, Text
)
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import html
import networkx as nx


class Visualiser:
    """
    The Visualiser class bridges the different concerns to provide
    a simple interface through which the graph can be updated,
    and retrieved in HTML format.
    """
    GRAPH_SIZE_PX: int = 600  # in px, needs to be equal for height and width otherwise calculations are wrong
    GRAPH_PADDING_PERC: int = 15  # %
    MAX_VERTEX_NAME_LEN: int = 20  # no. of characters

    def __init__(self):
        self.graph = ScenarioGraph()

    def update_visualisation(self, info: TraceInfo):
        self.graph.update_visualisation(info)

    def set_start(self, scenario: ScenarioInfo):
        self.graph.set_starting_node(scenario)

    def set_end(self, scenario: ScenarioInfo):
        self.graph.set_ending_node(scenario)

    def generate_visualisation(self) -> str:
        self.graph.calculate_pos()
        networkvisualiser = NetworkVisualiser(self.graph)
        html_bokeh = networkvisualiser.generate_html()
        return f"<iframe srcdoc=\"{html.escape(html_bokeh)}\", width=\"{Visualiser.GRAPH_SIZE_PX}px\", height=\"{Visualiser.GRAPH_SIZE_PX}px\"></iframe>"


class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    EDGE_WIDTH: float = 2.0
    EDGE_ALPHA: float = 0.7
    EDGE_COLOUR: str | tuple[int, int, int] = (
        12, 12, 12)  # 'visual studio black'

    def __init__(self, graph: ScenarioGraph):
        self.plot = None
        self.graph = graph
        self.labels = dict(x=[], y=[], label=[])

        # graph customisation options
        self.node_radius = 1.0
        self.char_width = 0.1
        self.char_height = 0.1

    def generate_html(self) -> str:
        """
        Generate html file from networkx graph via Bokeh
        """
        self._initialise_plot()
        self._add_nodes_with_labels()
        self._add_edges()
        return file_html(self.plot, CDN, "graph")

    def _initialise_plot(self):
        """
        Define plot with width, height, x_range, y_range and enable tools.
        x_range and y_range are padded. Plot needs to be a square
        """
        padding: float = Visualiser.GRAPH_PADDING_PERC / 100

        x_range, y_range = zip(*self.graph.pos.values())
        x_min = min(x_range) - padding * (max(x_range) - min(x_range))
        x_max = max(x_range) + padding * (max(x_range) - min(x_range))
        y_min = min(y_range) - padding * (max(y_range) - min(y_range))
        y_max = max(y_range) + padding * (max(y_range) - min(y_range))

        # scale node radius based on range
        nodes_range = max(x_max-x_min, y_max-y_min)
        self.node_radius = nodes_range / 50
        self.char_width = nodes_range / 100
        self.char_height = nodes_range / 75

        # create plot
        x_range = Range1d(min(x_min, y_min), max(x_max, y_max))
        y_range = Range1d(min(x_min, y_min), max(x_max, y_max))

        self.plot = Plot(width=Visualiser.GRAPH_SIZE_PX,
                         height=Visualiser.GRAPH_SIZE_PX,
                         x_range=x_range,
                         y_range=y_range)

        # add tools
        self.plot.add_tools(ResetTool(), SaveTool(),
                            WheelZoomTool(), PanTool())

    def _calculate_text_dimensions(self, text: str) -> tuple[float, float]:
        """Calculate width and height needed for text based on actual text length"""
        text_length = len(text)
        width = (text_length * self.char_width) + (2 * self.char_width)
        height = self.char_height + (2 * self.char_height)
        return width, height

    def _add_nodes_with_labels(self):
        """
        Add nodes with text labels inside them
        """
        node_labels = nx.get_node_attributes(self.graph.networkx, "label")
        
        # Create data sources for nodes and labels
        circle_data = dict(x=[], y=[], radius=[], label=[])
        rect_data = dict(x=[], y=[], width=[], height=[], label=[])
        text_data = dict(x=[], y=[], text=[])
        
        for node in self.graph.networkx.nodes:
            label = node_labels.get(node, str(node))
            if isinstance(label, list):
                label = label[0] if label else str(node)
            
            label = self._cap_name(label)
            x, y = self.graph.pos[node]
            
            if node == 'start':
                # Start node remains as circle
                circle_data['x'].append(x)
                circle_data['y'].append(y)
                circle_data['radius'].append(self.node_radius)
                circle_data['label'].append(label)
            else:
                # Scenario nodes as rectangles
                text_width, text_height = self._calculate_text_dimensions(label)
                
                rect_data['x'].append(x)
                rect_data['y'].append(y)
                rect_data['width'].append(text_width)
                rect_data['height'].append(text_height)
                rect_data['label'].append(label)
            
            # Add text for all nodes
            text_data['x'].append(x)
            text_data['y'].append(y)
            text_data['text'].append(label)
        
        # Add circles for start node
        if circle_data['x']:
            circle_source = ColumnDataSource(circle_data)
            circles = Circle(x='x', y='y', radius='radius', 
                           fill_color=Spectral4[0])
            self.plot.add_glyph(circle_source, circles)
        
        # Add rectangles for scenario nodes
        if rect_data['x']:
            rect_source = ColumnDataSource(rect_data)
            rectangles = Rect(x='x', y='y', width='width', height='height',
                            fill_color=Spectral4[0])
            self.plot.add_glyph(rect_source, rectangles)
        
        # Add text labels for all nodes
        text_source = ColumnDataSource(text_data)
        text_labels = Text(x='x', y='y', text='text',
                          text_align='center', text_baseline='middle',
                          text_color='white', text_font_size='9pt')
        self.plot.add_glyph(text_source, text_labels)

    def add_self_loop(self, x: float, y: float, label: str):
        """
        Self-loop as a Bezier curve with arrow head
        """
        loop = Bezier(
            # starting point
            x0=x + self.node_radius,
            y0=y,

            # end point
            x1=x,
            y1=y - self.node_radius,

            # control points
            cx0=x + 5*self.node_radius,
            cy0=y,
            cx1=x,
            cy1=y - 5*self.node_radius,

            # styling
            line_color=NetworkVisualiser.EDGE_COLOUR,
            line_width=NetworkVisualiser.EDGE_WIDTH,
            line_alpha=NetworkVisualiser.EDGE_ALPHA,
        )
        self.plot.add_glyph(loop)

        # add arrow head
        arrow = Arrow(
            end=NormalHead(size=10,
                           line_color=NetworkVisualiser.EDGE_COLOUR,
                           fill_color=NetworkVisualiser.EDGE_COLOUR),

            # -0.01 to guarantee that arrow points upwards.
            x_start=x, y_start=y-self.node_radius-0.01,
            x_end=x, y_end=y-self.node_radius
        )

        # add edge label
        self.labels['x'].append(x + self.node_radius)
        self.labels['y'].append(y - 4*self.node_radius)
        self.labels['label'].append(label)

        self.plot.add_layout(arrow)

    def _add_edges(self):
        edge_labels = nx.get_edge_attributes(self.graph.networkx, "label")
        for edge in self.graph.networkx.edges():
            x0, y0 = self.graph.pos[edge[0]]
            x1, y1 = self.graph.pos[edge[1]]
            if edge[0] == edge[1]:
                self.add_self_loop(
                    x=x0, y=y0, label=self._cap_name(edge_labels[edge]))

            else:
                # edge between 2 different nodes
                dx = x1 - x0
                dy = y1 - y0

                length = sqrt(dx**2 + dy**2)

                arrow = Arrow(
                    end=NormalHead(
                        size=10,
                        line_color=NetworkVisualiser.EDGE_COLOUR,
                        fill_color=NetworkVisualiser.EDGE_COLOUR),

                    x_start=x0 + dx / length * self.node_radius,
                    y_start=y0 + dy / length * self.node_radius,
                    x_end=x1 - dx / length * self.node_radius,
                    y_end=y1 - dy / length * self.node_radius
                )

                self.plot.add_layout(arrow)

                # add edge label
                self.labels['x'].append((x0+x1)/2)
                self.labels['y'].append((y0+y1)/2)
                self.labels['label'].append(self._cap_name(edge_labels[edge]))

    @staticmethod
    def _cap_name(name: str) -> str:
        if len(name) < Visualiser.MAX_VERTEX_NAME_LEN:
            return name

        return f"{name[:(Visualiser.MAX_VERTEX_NAME_LEN-3)]}..."