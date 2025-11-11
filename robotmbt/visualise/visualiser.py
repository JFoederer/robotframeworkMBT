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
        self.node_props = {}  # Store node properties for arrow calculations

        # graph customisation options
        self.node_radius = 1.0
        self.char_width = 0.1
        self.char_height = 0.1
        self.padding = 0.1

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
        self.node_radius = nodes_range / 150
        self.char_width = nodes_range / 150   
        self.char_height = nodes_range / 150

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
        # Calculate width based on character count
        text_length = len(text)
        width = (text_length * self.char_width) + (2 * self.padding)
        
        # Reduced height for more compact rectangles
        height = self.char_height + (self.padding)
        
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
            # Ensure label is a string, not a list
            label = node_labels.get(node, str(node))  # Use node as fallback if no label
            if isinstance(label, list):
                label = label[0] if label else str(node)
            
            label = self._cap_name(label)
            x, y = self.graph.pos[node]
            
            if node == 'start':
                # For start node (circle), calculate diameter based on text width
                text_width, text_height = self._calculate_text_dimensions(label)
                # Use text width + padding as diameter, then divide by 2 for radius
                radius = (text_width / 2.5)
                
                circle_data['x'].append(x)
                circle_data['y'].append(y)
                circle_data['radius'].append(radius)
                circle_data['label'].append(label)
                
                # Store node properties for arrow calculations
                self.node_props[node] = {'type': 'circle', 'x': x, 'y': y, 'radius': radius, 'label': label}
                
            else:
                # For scenario nodes (rectangles), calculate dimensions based on text
                text_width, text_height = self._calculate_text_dimensions(label)
                
                rect_data['x'].append(x)
                rect_data['y'].append(y)
                rect_data['width'].append(text_width)
                rect_data['height'].append(text_height)
                rect_data['label'].append(label)
                
                # Store node properties for arrow calculations
                self.node_props[node] = {'type': 'rect', 'x': x, 'y': y, 'width': text_width, 'height': text_height, 'label': label}
            
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

    def _get_edge_points(self, start_node, end_node):
        """Calculate edge start and end points at node borders"""
        start_props = self.node_props.get(start_node)
        end_props = self.node_props.get(end_node)
        
        if not start_props or not end_props:
            return start_node, start_node, end_node, end_node  # Fallback
        
        # Calculate direction vector
        dx = end_props['x'] - start_props['x']
        dy = end_props['y'] - start_props['y']
        distance = sqrt(dx*dx + dy*dy)
        
        if distance == 0:  # Same node (self-loop handled separately)
            return start_props['x'], start_props['y'], end_props['x'], end_props['y']
        
        # Normalize direction vector
        dx /= distance
        dy /= distance
        
        # Calculate start point at border
        if start_props['type'] == 'circle':
            start_x = start_props['x'] + dx * start_props['radius']
            start_y = start_props['y'] + dy * start_props['radius']
        else:  # rectangle
            # For rectangles, we need to find where the line intersects the rectangle border
            rect_width = start_props['width']
            rect_height = start_props['height']
            
            # Calculate scaling factors for x and y directions
            scale_x = rect_width / (2 * abs(dx)) if dx != 0 else float('inf')
            scale_y = rect_height / (2 * abs(dy)) if dy != 0 else float('inf')
            
            # Use the smaller scale to ensure we hit the border
            scale = min(scale_x, scale_y)
            
            start_x = start_props['x'] + dx * scale
            start_y = start_props['y'] + dy * scale
        
        # Calculate end point at border (reverse direction)
        if end_props['type'] == 'circle':
            end_x = end_props['x'] - dx * end_props['radius']
            end_y = end_props['y'] - dy * end_props['radius']
        else:  # rectangle
            rect_width = end_props['width']
            rect_height = end_props['height']
            
            # Calculate scaling factors for x and y directions (reverse)
            scale_x = rect_width / (2 * abs(dx)) if dx != 0 else float('inf')
            scale_y = rect_height / (2 * abs(dy)) if dy != 0 else float('inf')
            
            # Use the smaller scale to ensure we hit the border
            scale = min(scale_x, scale_y)
            
            end_x = end_props['x'] - dx * scale
            end_y = end_props['y'] - dy * scale
        
        return start_x, start_y, end_x, end_y

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
        edge_text = Text(
            x=x + self.node_radius, 
            y=y - 4*self.node_radius, 
            text=label,
            text_align='center', 
            text_baseline='middle',
            text_font_size='7pt'
        )
        self.plot.add_glyph(edge_text)

        self.plot.add_layout(arrow)

    def _add_edges(self):
        edge_labels = nx.get_edge_attributes(self.graph.networkx, "label")
        
        # Create data sources for edges and edge labels
        edge_text_data = dict(x=[], y=[], text=[])
        
        for edge in self.graph.networkx.edges():
            edge_label = edge_labels.get(edge, "")
            if isinstance(edge_label, list):
                edge_label = edge_label[0] if edge_label else ""
            edge_label = self._cap_name(edge_label)
            
            if edge[0] == edge[1]:
                # Self-loop handled separately
                x, y = self.graph.pos[edge[0]]
                self.add_self_loop(x=x, y=y, label=edge_label)
            else:
                # Calculate edge points at node borders
                start_x, start_y, end_x, end_y = self._get_edge_points(edge[0], edge[1])
                
                # Add arrow between the calculated points
                arrow = Arrow(
                    end=NormalHead(
                        size=6,
                        line_color=NetworkVisualiser.EDGE_COLOUR,
                        fill_color=NetworkVisualiser.EDGE_COLOUR),
                    x_start=start_x, y_start=start_y,
                    x_end=end_x, y_end=end_y
                )
                self.plot.add_layout(arrow)

                # Collect edge label data (position at midpoint)
                edge_text_data['x'].append((start_x + end_x) / 2)
                edge_text_data['y'].append((start_y + end_y) / 2)
                edge_text_data['text'].append(edge_label)
        
        # Add all edge labels at once
        if edge_text_data['x']:
            edge_text_source = ColumnDataSource(edge_text_data)
            edge_labels_glyph = Text(x='x', y='y', text='text',
                                   text_align='center', text_baseline='middle',
                                   text_font_size='7pt')
            self.plot.add_glyph(edge_text_source, edge_labels_glyph)

    @staticmethod
    def _cap_name(name: str) -> str:
        if len(name) < Visualiser.MAX_VERTEX_NAME_LEN:
            return name

        return f"{name[:(Visualiser.MAX_VERTEX_NAME_LEN-3)]}..."