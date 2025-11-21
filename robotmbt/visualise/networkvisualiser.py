from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.stategraph import StateGraph
from bokeh.palettes import Spectral4
from bokeh.models import (
    Plot, Range1d, Circle, Rect,
    Arrow, NormalHead,
    Bezier, ColumnDataSource, ResetTool,
    SaveTool, WheelZoomTool, PanTool, Text
)
from bokeh.embed import file_html
from bokeh.resources import CDN
from math import sqrt
import networkx as nx


class NetworkVisualiser:
    """
    Generate plot with Bokeh
    """

    ARROWHEAD_SIZE: int = 6  # Consistent arrowhead size
    EDGE_WIDTH: float = 2.0
    EDGE_ALPHA: float = 0.7
    EDGE_COLOUR: str | tuple[int, int, int] = (
        12, 12, 12)  # 'visual studio black'
    GRAPH_PADDING_PERC: int = 15  # %
    # in px, needs to be equal for height and width otherwise calculations are wrong
    GRAPH_SIZE_PX: int = 600
    MAX_VERTEX_NAME_LEN: int = 20  # no. of characters

    def __init__(self, graph: AbstractGraph):
        self.plot = None
        self.graph = graph
        self.node_props = {}  # Store node properties for arrow calculations
        self.graph_layout = {}

        # graph customisation options
        self.node_radius = 1.0
        self.char_width = 0.1
        self.char_height = 0.1
        self.padding = 0.1

    def generate_html(self) -> str:
        """
        Generate html file from networkx graph via Bokeh
        """
        self._calculate_graph_layout()
        self._initialise_plot()
        self._add_nodes_with_labels()
        self._add_edges()
        return file_html(self.plot, CDN, "graph")

    def _initialise_plot(self):
        """
        Define plot with width, height, x_range, y_range and enable tools.
        x_range and y_range are padded. Plot needs to be a square
        """
        padding: float = self.GRAPH_PADDING_PERC / 100

        x_range, y_range = zip(*self.graph_layout.values())
        x_min = min(x_range) - padding * (max(x_range) - min(x_range))
        x_max = max(x_range) + padding * (max(x_range) - min(x_range))
        y_min = min(y_range) - padding * (max(y_range) - min(y_range))
        y_max = max(y_range) + padding * (max(y_range) - min(y_range))

        # scale node radius based on range
        nodes_range = max(x_max - x_min, y_max - y_min)
        self.node_radius = nodes_range / 150
        self.char_width = nodes_range / 150
        self.char_height = nodes_range / 150

        # create plot
        x_range = Range1d(min(x_min, y_min), max(x_max, y_max))
        y_range = Range1d(min(x_min, y_min), max(x_max, y_max))

        self.plot = Plot(width=self.GRAPH_SIZE_PX,
                         height=self.GRAPH_SIZE_PX,
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
        height = self.char_height + self.padding

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
            # Labels are always defined and cannot be lists
            label = node_labels[node]
            label = self._cap_name(label)
            x, y = self.graph_layout[node]

            if node == 'start':
                # For start node (circle), calculate radius based on text width
                text_width, text_height = self._calculate_text_dimensions(
                    label)
                # Calculate radius from text dimensions
                radius = (text_width / 2.5)

                circle_data['x'].append(x)
                circle_data['y'].append(y)
                circle_data['radius'].append(radius)
                circle_data['label'].append(label)

                # Store node properties for arrow calculations
                self.node_props[node] = {
                    'type': 'circle', 'x': x, 'y': y, 'radius': radius, 'label': label}

            else:
                # For scenario nodes (rectangles), calculate dimensions based on text
                text_width, text_height = self._calculate_text_dimensions(
                    label)

                rect_data['x'].append(x)
                rect_data['y'].append(y)
                rect_data['width'].append(text_width)
                rect_data['height'].append(text_height)
                rect_data['label'].append(label)

                # Store node properties for arrow calculations
                self.node_props[node] = {'type': 'rect', 'x': x, 'y': y, 'width': text_width, 'height': text_height,
                                         'label': label}

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

        # Node properties should always exist
        if not start_props or not end_props:
            raise ValueError(
                f"Node properties not found for nodes: {start_node}, {end_node}")

        # Calculate direction vector
        dx = end_props['x'] - start_props['x']
        dy = end_props['y'] - start_props['y']
        distance = sqrt(dx * dx + dy * dy)

        # Self-loops are handled separately, distance should never be 0
        if distance == 0:
            raise ValueError(
                "Distance between different nodes should not be zero")

        # Normalize direction vector
        dx /= distance
        dy /= distance

        # Calculate start point at border
        if start_props['type'] == 'circle':
            start_x = start_props['x'] + dx * start_props['radius']
            start_y = start_props['y'] + dy * start_props['radius']
        else:
            # Find where the line intersects the rectangle border
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
        # End nodes should never be circles for regular edges
        if end_props['type'] == 'circle':
            raise ValueError(
                f"End node should not be a circle for regular edges: {end_node}")
        else:
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

    def add_self_loop(self, node_id: str):
        """
        Circular arc that starts and ends at the top side of the rectangle
        Start at 1/4 width, end at 3/4 width, with a circular arc above
        The arc itself ends with the arrowhead pointing into the rectangle
        """
        # Get node properties directly by node ID
        node_props = self.node_props.get(node_id)

        # Node properties should always exist
        if node_props is None:
            raise ValueError(f"Node properties not found for node: {node_id}")

        # Self-loops should only be for rectangle nodes (scenarios)
        if node_props['type'] != 'rect':
            raise ValueError(
                f"Self-loops should only be for rectangle nodes, got: {node_props['type']}")

        x, y = node_props['x'], node_props['y']
        width = node_props['width']
        height = node_props['height']

        # Start: 1/4 width from left, top side
        start_x = x - width / 4
        start_y = y + height / 2

        # End: 3/4 width from left, top side
        end_x = x + width / 4
        end_y = y + height / 2

        # Arc height above the rectangle
        arc_height = width * 0.4

        # Control points for a circular arc above
        control1_x = x - width / 8
        control1_y = y + height / 2 + arc_height

        control2_x = x + width / 8
        control2_y = y + height / 2 + arc_height

        # Create the Bezier curve (the main arc) with the same thickness as straight lines
        loop = Bezier(
            x0=start_x, y0=start_y,
            x1=end_x, y1=end_y,
            cx0=control1_x, cy0=control1_y,
            cx1=control2_x, cy1=control2_y,
            line_color=NetworkVisualiser.EDGE_COLOUR,
            line_width=NetworkVisualiser.EDGE_WIDTH,
            line_alpha=NetworkVisualiser.EDGE_ALPHA,
        )
        self.plot.add_glyph(loop)

        # Calculate the tangent direction at the end of the Bezier curve
        # For a cubic Bezier, the tangent at the end point is from the last control point to the end point
        tangent_x = end_x - control2_x
        tangent_y = end_y - control2_y

        # Normalize the tangent vector
        tangent_length = sqrt(tangent_x ** 2 + tangent_y ** 2)
        if tangent_length > 0:
            tangent_x /= tangent_length
            tangent_y /= tangent_length

        # Add just the arrowhead (NormalHead) at the end point, oriented along the tangent
        arrowhead = NormalHead(
            size=NetworkVisualiser.ARROWHEAD_SIZE,
            line_color=NetworkVisualiser.EDGE_COLOUR,
            fill_color=NetworkVisualiser.EDGE_COLOUR,
            line_width=NetworkVisualiser.EDGE_WIDTH
        )

        # Create a standalone arrowhead at the end point
        # Strategy: use a very short Arrow that's essentially just the head
        arrow = Arrow(
            end=arrowhead,
            x_start=end_x - tangent_x * 0.001,  # Almost zero length line
            y_start=end_y - tangent_y * 0.001,
            x_end=end_x,
            y_end=end_y,
            line_color=NetworkVisualiser.EDGE_COLOUR,
            line_width=NetworkVisualiser.EDGE_WIDTH,
            line_alpha=NetworkVisualiser.EDGE_ALPHA
        )
        self.plot.add_layout(arrow)

        # Add edge label - positioned above the arc
        label_x = x
        label_y = y + height / 2 + arc_height * 0.6

        return label_x, label_y

    def _add_edges(self):
        edge_labels = nx.get_edge_attributes(self.graph.networkx, "label")

        # Create data sources for edges and edge labels
        edge_text_data = dict(x=[], y=[], text=[])

        for edge in self.graph.networkx.edges():
            # Edge labels are always defined and cannot be lists
            edge_label = edge_labels[edge]
            edge_label = self._cap_name(edge_label)
            edge_text_data['text'].append(edge_label)

            if edge[0] == edge[1]:
                # Self-loop handled separately
                label_x, label_y = self.add_self_loop(edge[0])
                edge_text_data['x'].append(label_x)
                edge_text_data['y'].append(label_y)

            else:
                # Calculate edge points at node borders
                start_x, start_y, end_x, end_y = self._get_edge_points(
                    edge[0], edge[1])

                # Add arrow between the calculated points
                arrow = Arrow(
                    end=NormalHead(
                        size=NetworkVisualiser.ARROWHEAD_SIZE,
                        line_color=NetworkVisualiser.EDGE_COLOUR,
                        fill_color=NetworkVisualiser.EDGE_COLOUR),
                    x_start=start_x, y_start=start_y,
                    x_end=end_x, y_end=end_y
                )
                self.plot.add_layout(arrow)

                # Collect edge label data (position at midpoint)
                edge_text_data['x'].append((start_x + end_x) / 2)
                edge_text_data['y'].append((start_y + end_y) / 2)

        # Add all edge labels at once
        if edge_text_data['x']:
            edge_text_source = ColumnDataSource(edge_text_data)
            edge_labels_glyph = Text(x='x', y='y', text='text',
                                     text_align='center', text_baseline='middle',
                                     text_font_size='7pt')
            self.plot.add_glyph(edge_text_source, edge_labels_glyph)

    def _cap_name(self, name: str) -> str:
        if len(name) < self.MAX_VERTEX_NAME_LEN or isinstance(self.graph, StateGraph):
            return name

        return f"{name[:(self.MAX_VERTEX_NAME_LEN - 3)]}..."

    def _calculate_graph_layout(self):
        try:
            self.graph_layout = nx.bfs_layout(
                self.graph.networkx, 'start', align='horizontal')
            # horizontal mirror
            for node in self.graph_layout:
                self.graph_layout[node] = (self.graph_layout[node][0],
                                           -1 * self.graph_layout[node][1])
        except nx.NetworkXException:
            # if planar layout cannot find a graph without crossing edges
            self.graph_layout = nx.arf_layout(self.graph.networkx, seed=42)
