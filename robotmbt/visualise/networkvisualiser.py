from bokeh.core.enums import PlaceType, LegendLocationType
from bokeh.core.property.vectorization import value
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource, Rect, Text, ResetTool, SaveTool, WheelZoomTool, PanTool, Plot, Range1d, \
    Title, FullscreenTool, CustomJS, Segment, Arrow, NormalHead, Bezier, Legend, BoxZoomTool

from grandalf.graphs import Vertex as GVertex, Edge as GEdge, Graph as GGraph
from grandalf.layouts import SugiyamaLayout

from networkx import DiGraph

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph

# Padding within the nodes between the borders and inner text
HORIZONTAL_PADDING_WITHIN_NODES: int = 5
VERTICAL_PADDING_WITHIN_NODES: int = 5

# Colors for different parts of the graph
FINAL_TRACE_NODE_COLOR: str = '#CCCC00'
OTHER_NODE_COLOR: str = '#999989'
FINAL_TRACE_EDGE_COLOR: str = '#444422'
OTHER_EDGE_COLOR: str = '#BBBBAA'

# Legend placement
# Alignment within graph ('center' is in the middle, 'top_right' is the top right, etc.)
LEGEND_LOCATION: LegendLocationType | tuple[float, float] = 'top_right'
# Where it appears relative to graph ('center' is within, 'below' is below, etc.)
LEGEND_PLACE: PlaceType = 'center'

# Dimensions of the plot in the window
INNER_WINDOW_WIDTH: int = 720
INNER_WINDOW_HEIGHT: int = 480
OUTER_WINDOW_WIDTH: int = INNER_WINDOW_WIDTH + (280 if LEGEND_PLACE == 'left' or LEGEND_PLACE == 'right' else 30)
OUTER_WINDOW_HEIGHT: int = INNER_WINDOW_HEIGHT + (150 if LEGEND_PLACE == 'below' or LEGEND_PLACE == 'center' else 30)

# Font sizes
MAJOR_FONT_SIZE: int = 16
MINOR_FONT_SIZE: int = 8


class Node:
    """
    Contains the information we need to add a node to the graph.
    """

    def __init__(self, node_id: str, label: str, x: int, y: int, width: float, height: float):
        self.node_id = node_id
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Edge:
    """
    Contains the information we need to add an edge to the graph.
    """

    def __init__(self, from_node: str, to_node: str, label: str, points: list[tuple[float, float]]):
        self.from_node = from_node
        self.to_node = to_node
        self.label = label
        self.points = points


class NetworkVisualiser:
    """
    A container for a Bokeh graph, which can be created from any abstract graph.
    """

    def __init__(self, graph: AbstractGraph, suite_name: str, seed: str):
        # Extract what we need from the graph
        self.networkx: DiGraph = graph.networkx
        self.final_trace = graph.get_final_trace()
        self.start = graph.start_node

        # Set up a Bokeh figure
        self.plot = Plot(width=OUTER_WINDOW_WIDTH, height=OUTER_WINDOW_HEIGHT)
        self.plot.output_backend = "svg"

        # Create Sugiyama layout
        nodes, edges = self._create_layout()
        self.node_dict: dict[str, Node] = {}
        for node in nodes:
            self.node_dict[node.node_id] = node

        # Keep track of arrows in the graph for scaling
        self.arrows = []

        # Add the nodes to the graph
        self._add_nodes(nodes)

        # Add the edges to the graph
        self._add_edges(nodes, edges)

        # Add a legend to the graph
        self._add_legend(graph)

        # Add our features to the graph (e.g. tools)
        self._add_features(suite_name, seed)

    def generate_html(self):
        """
        Generate HTML for the Bokeh graph.
        """
        return file_html(self.plot, 'inline', "graph")

    def _add_nodes(self, nodes: list[Node]):
        """
        Add the nodes to the graph in the form of Rect and Text glyphs.
        """
        # The ColumnDataSources to store our nodes and edges in Bokeh's format
        node_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'w': [], 'h': [], 'color': []})
        node_label_source: ColumnDataSource = ColumnDataSource(
            {'id': [], 'x': [], 'y': [], 'label': []})

        # Add all nodes to the column data sources
        for node in nodes:
            _add_node_to_sources(node, self.final_trace, node_source, node_label_source)

        # Add the glyphs for nodes and their labels
        node_glyph = Rect(x='x', y='y', width='w', height='h', fill_color='color')
        self.plot.add_glyph(node_source, node_glyph)

        node_label_glyph = Text(x='x', y='y', text='label', text_align='left', text_baseline='middle',
                                text_font_size=f'{MAJOR_FONT_SIZE}pt', text_font=value("Courier New"))
        node_label_glyph.tags = [f"scalable_text{MAJOR_FONT_SIZE}"]
        self.plot.add_glyph(node_label_source, node_label_glyph)

    def _add_edges(self, nodes: list[Node], edges: list[Edge]):
        """
        Add the edges to the graph in the form of Arrow layouts and Segment, Bezier, and Text glyphs.
        """
        # The ColumnDataSources to store our edges in Bokeh's format
        edge_part_source: ColumnDataSource = ColumnDataSource(
            {'from': [], 'to': [], 'start_x': [], 'start_y': [], 'end_x': [], 'end_y': [], 'color': []})
        edge_arrow_source: ColumnDataSource = ColumnDataSource(
            {'from': [], 'to': [], 'start_x': [], 'start_y': [], 'end_x': [], 'end_y': [], 'color': []})
        edge_bezier_source: ColumnDataSource = ColumnDataSource(
            {'from': [], 'to': [], 'start_x': [], 'start_y': [], 'end_x': [], 'end_y': [], 'control1_x': [],
             'control1_y': [], 'control2_x': [], 'control2_y': [], 'color': []})
        edge_label_source: ColumnDataSource = ColumnDataSource({'from': [], 'to': [], 'x': [], 'y': [], 'label': []})

        for edge in edges:
            _add_edge_to_sources(nodes, edge, self.final_trace, edge_part_source, edge_arrow_source, edge_bezier_source,
                                 edge_label_source)

        # Add the glyphs for edges and their labels
        edge_part_glyph = Segment(x0='start_x', y0='start_y', x1='end_x', y1='end_y', line_color='color')
        self.plot.add_glyph(edge_part_source, edge_part_glyph)

        arrow_layout = Arrow(
            end=NormalHead(size=10, fill_color='color', line_color='color'),
            x_start='start_x', y_start='start_y',
            x_end='end_x', y_end='end_y', line_color='color',
            source=edge_arrow_source
        )
        self.plot.add_layout(arrow_layout)
        self.arrows.append(arrow_layout)

        edge_bezier_glyph = Bezier(x0='start_x', y0='start_y', x1='end_x', y1='end_y', cx0='control1_x',
                                   cy0='control1_y', cx1='control2_x', cy1='control2_y', line_color='color')
        self.plot.add_glyph(edge_bezier_source, edge_bezier_glyph)

        edge_label_glyph = Text(x='x', y='y', text='label', text_align='center', text_baseline='middle',
                                text_font_size=f'{MINOR_FONT_SIZE}pt', text_font=value("Courier New"))
        edge_label_glyph.tags = [f"scalable_text{MINOR_FONT_SIZE}"]
        self.plot.add_glyph(edge_label_source, edge_label_glyph)

    def _create_layout(self) -> tuple[list[Node], list[Edge]]:
        """
        Create the Sugiyama layout using grandalf.
        """
        # Containers to convert networkx nodes/edges to the proper format.
        vertices = []
        edges = []
        flips = []

        # Extract nodes from networkx and put them in the proper format to be used by grandalf.
        start = None
        for node_id in self.networkx.nodes:
            v = GVertex(node_id)
            w, h = _calculate_dimensions(self.networkx.nodes[node_id]['label'])
            v.view = NodeView(w, h)
            vertices.append(v)
            if node_id == self.start:
                start = v

        # Calculate which edges need to be flipped to make the graph acyclic.
        flip = _flip_edges([e for e in self.networkx.edges])

        # Extract edges from networkx and put them in the proper format to be used by grandalf.
        for (from_id, to_id) in self.networkx.edges:
            from_node = _find_node(vertices, from_id)
            to_node = _find_node(vertices, to_id)
            e = GEdge(from_node, to_node)
            e.view = EdgeView()
            edges.append(e)
            if (from_id, to_id) in flip:
                flips.append(e)

        # Feed the info to grandalf and get the layout.
        g = GGraph(vertices, edges)

        sugiyama = SugiyamaLayout(g.C[0])
        sugiyama.init_all(roots=[start], inverted_edges=flips)
        sugiyama.draw()

        # Extract the information we need from the nodes and edges and return them in our format.
        ns = []
        for v in g.C[0].sV:
            node_id = v.data
            label = self.networkx.nodes[node_id]['label']
            (x, y) = v.view.xy
            (w, h) = _calculate_dimensions(label)
            ns.append(Node(node_id, label, x, -y, w, h))

        es = []
        for e in g.C[0].sE:
            from_id = e.v[0].data
            to_id = e.v[1].data
            label = self.networkx.edges[(from_id, to_id)]['label']
            points = []
            # invert y axis
            for p in e.view.points:
                points.append((p[0], -p[1]))

            es.append(Edge(from_id, to_id, label, points))

        return ns, es

    def _add_features(self, suite_name: str, seed: str):
        """
        Add our features to the graph such as tools, titles, and JavaScript callbacks.
        """
        if seed != "":
            self.plot.add_layout(Title(text="seed=" + seed, align="center", text_color="#999999"), "above")
        self.plot.add_layout(Title(text=suite_name, align="center"), "above")

        # Add the different tools
        wheel_zoom = WheelZoomTool()
        self.plot.add_tools(ResetTool(), SaveTool(),
                            wheel_zoom, PanTool(),
                            FullscreenTool(), BoxZoomTool())
        self.plot.toolbar.active_scroll = wheel_zoom

        # Specify the default range - these values represent the aspect ratio of the actual view in the window
        self.plot.x_range = Range1d(-INNER_WINDOW_WIDTH / 2, INNER_WINDOW_WIDTH / 2)
        self.plot.y_range = Range1d(-INNER_WINDOW_HEIGHT + (0 if seed == '' else 20), 0)
        self.plot.x_range.tags = [{"initial_span": INNER_WINDOW_WIDTH}]
        self.plot.y_range.tags = [{"initial_span": INNER_WINDOW_HEIGHT - (0 if seed == '' else 20)}]

        # A JS callback to scale text and arrows, and change aspect ratio.
        resize_cb = CustomJS(args=dict(xr=self.plot.x_range, yr=self.plot.y_range, plot=self.plot, arrows=self.arrows),
                             code=f"""
    // Initialize initial scale tag
    if (!plot.tags || plot.tags.length === 0) {{
        plot.tags = [{{
            initial_scale: plot.inner_height / (yr.end - yr.start)
        }}]
    }}

    // Calculate current x and y span
    const xspan = xr.end - xr.start;
    const yspan = yr.end - yr.start;

    // Calculate inner aspect ratio and span aspect ratio
    const inner_aspect = plot.inner_width / plot.inner_height;
    const span_aspect = xspan / yspan;

    // Let span aspect ratio match inner aspect ratio if needed
    if (Math.abs(inner_aspect - span_aspect) > 0.05) {{
        const xmid = xr.start + xspan / 2;
        const new_xspan = yspan * inner_aspect;
        xr.start = xmid - new_xspan / 2;
        xr.end = xmid + new_xspan / 2;
    }}

    // Calculate scale factor
    const scale = (plot.inner_height / yspan) / plot.tags[0].initial_scale

    // Scale text
    for (const r of plot.renderers) {{
        if (!r.glyph || !r.glyph.tags) continue

        if (r.glyph.tags.includes("scalable_text{MAJOR_FONT_SIZE}")) {{
            r.glyph.text_font_size = Math.floor({MAJOR_FONT_SIZE} * scale) + "pt"
        }}

        if (r.glyph.tags.includes("scalable_text{MINOR_FONT_SIZE}")) {{
            r.glyph.text_font_size = Math.floor({MINOR_FONT_SIZE} * scale) + "pt"
        }}
    }}

    // Scale arrows
    for (const a of arrows) {{
        if (!a.properties) continue;
        if (!a.properties.end) continue;
        if (!a.properties.end._value) continue;
        if (!a.properties.end._value.properties) continue;
        if (!a.properties.end._value.properties.size) continue;
        if (!a.properties.end._value.properties.size._value) continue;
        if (!a.properties.end._value.properties.size._value.value) continue;
        if (a._base_end_size == null)
            a._base_end_size = a.properties.end._value.properties.size._value.value;
        a.properties.end._value.properties.size._value.value = a._base_end_size * Math.sqrt(scale);
        a.change.emit();
    }}""")

        # Add the callback to the values that change when zooming/resizing.
        self.plot.x_range.js_on_change("start", resize_cb)
        self.plot.x_range.js_on_change("end", resize_cb)
        self.plot.y_range.js_on_change("start", resize_cb)
        self.plot.y_range.js_on_change("end", resize_cb)
        self.plot.js_on_change("inner_width", resize_cb)
        self.plot.js_on_change("inner_height", resize_cb)

    def _add_legend(self, graph: AbstractGraph):
        """
        Adds a legend to the graph with the node/edge information from the given graph.
        """
        empty_source = ColumnDataSource({'_': [0]})

        final_trace_node_glyph = Rect(x='_', y='_', width='_', height='_', fill_color=FINAL_TRACE_NODE_COLOR)
        final_trace_node = self.plot.add_glyph(empty_source, final_trace_node_glyph)

        other_node_glyph = Rect(x='_', y='_', width='_', height='_', fill_color=OTHER_NODE_COLOR)
        other_node = self.plot.add_glyph(empty_source, other_node_glyph)

        final_trace_edge_glyph = Segment(
            x0='_', x1='_',
            y0='_', y1='_', line_color=FINAL_TRACE_EDGE_COLOR
        )
        final_trace_edge = self.plot.add_glyph(empty_source, final_trace_edge_glyph)

        other_edge_glyph = Segment(
            x0='_', x1='_',
            y0='_', y1='_', line_color=OTHER_EDGE_COLOR
        )
        other_edge = self.plot.add_glyph(empty_source, other_edge_glyph)

        legend = Legend(items=[(graph.get_legend_info_final_trace_node(), [final_trace_node]),
                               (graph.get_legend_info_other_node(), [other_node]),
                               (graph.get_legend_info_final_trace_edge(), [final_trace_edge]),
                               (graph.get_legend_info_other_edge(), [other_edge])],
                        location=LEGEND_LOCATION, orientation="vertical")
        self.plot.add_layout(legend, LEGEND_PLACE)


class NodeView:
    """
    A view of a node in the format that grandalf expects.
    """

    def __init__(self, width: float, height: float):
        self.w, self.h = width, height
        self.xy = (0, 0)


class EdgeView:
    """
    A view of an edge in the format that grandalf expects.
    """

    def __init__(self):
        self.points = []

    def setpath(self, points: list[tuple[float, float]]):
        self.points = points


def _find_node(nodes: list[GVertex], node_id: str):
    """
    Find a node given its id in a list of grandalf nodes.
    """
    for node in nodes:
        if node.data == node_id:
            return node
    return None


def _get_connection_coordinates(nodes: list[Node], node_id: str) -> list[tuple[float, float]]:
    """
    Get the coordinates where edges can connect to a node given its id.
    These places are the middle of the left, right, top, and bottom edge, as well as the corners of the node.
    """
    start_possibilities = []

    # Get node from list
    node = None
    for n in nodes:
        if n.node_id == node_id:
            node = n
            break

    # Left
    start_possibilities.append((node.x - node.width / 2, node.y))
    # Right
    start_possibilities.append((node.x + node.width / 2, node.y))
    # Bottom
    start_possibilities.append((node.x, node.y - node.height / 2))
    # Top
    start_possibilities.append((node.x, node.y + node.height / 2))
    # Left bottom
    start_possibilities.append((node.x - node.width / 2, node.y - node.height / 2))
    # Left top
    start_possibilities.append((node.x - node.width / 2, node.y + node.height / 2))
    # Right bottom
    start_possibilities.append((node.x + node.width / 2, node.y - node.height / 2))
    # Right top
    start_possibilities.append((node.x + node.width / 2, node.y + node.height / 2))

    return start_possibilities


def _minimize_distance(from_pos: list[tuple[float, float]], to_pos: list[tuple[float, float]]) -> tuple[
        float, float, float, float]:
    """
    Find a pair of positions that minimizes their distance.
    """
    min_dist = -1
    fx, fy, tx, ty = 0, 0, 0, 0

    # Calculate the distance between all permutations
    for fp in from_pos:
        for tp in to_pos:
            distance = (fp[0] - tp[0]) ** 2 + (fp[1] - tp[1]) ** 2
            if min_dist == -1 or distance < min_dist:
                min_dist = distance
                fx, fy, tx, ty = fp[0], fp[1], tp[0], tp[1]

    # Return the permutation with the shortest distance
    return fx, fy, tx, ty


def _add_edge_to_sources(nodes: list[Node], edge: Edge, final_trace: list[str], edge_part_source: ColumnDataSource,
                         edge_arrow_source: ColumnDataSource, edge_bezier_source: ColumnDataSource,
                         edge_label_source: ColumnDataSource):
    """
    Add an edge between two nodes to the ColumnDataSources.
    Contains all logic to set their color, find their attachment points, and do self-loops properly.
    """
    in_final_trace = False
    for i in range(len(final_trace) - 1):
        if edge.from_node == final_trace[i] and edge.to_node == final_trace[i + 1]:
            in_final_trace = True
            break

    if edge.from_node == edge.to_node:
        _add_self_loop_to_sources(nodes, edge, in_final_trace, edge_arrow_source, edge_bezier_source, edge_label_source)
        return

    start_x, start_y = 0, 0
    end_x, end_y = 0, 0

    # Add edges going through the calculated points
    for i in range(len(edge.points) - 1):
        start_x, start_y = edge.points[i]
        end_x, end_y = edge.points[i + 1]

        # Collect possibilities where the edge can start and end
        if i == 0:
            from_possibilities = _get_connection_coordinates(nodes, edge.from_node)
        else:
            from_possibilities = [(start_x, start_y)]

        if i == len(edge.points) - 2:
            to_possibilities = _get_connection_coordinates(nodes, edge.to_node)
        else:
            to_possibilities = [(end_x, end_y)]

        # Choose connection points that minimize edge length
        start_x, start_y, end_x, end_y = _minimize_distance(from_possibilities, to_possibilities)

        if i < len(edge.points) - 2:
            # Middle part of edge without arrow
            edge_part_source.data['from'].append(edge.from_node)
            edge_part_source.data['to'].append(edge.to_node)
            edge_part_source.data['start_x'].append(start_x)
            edge_part_source.data['start_y'].append(start_y)
            edge_part_source.data['end_x'].append(end_x)
            edge_part_source.data['end_y'].append(end_y)
            edge_part_source.data['color'].append(FINAL_TRACE_EDGE_COLOR if in_final_trace else OTHER_EDGE_COLOR)
        else:
            # End of edge with arrow
            edge_arrow_source.data['from'].append(edge.from_node)
            edge_arrow_source.data['to'].append(edge.to_node)
            edge_arrow_source.data['start_x'].append(start_x)
            edge_arrow_source.data['start_y'].append(start_y)
            edge_arrow_source.data['end_x'].append(end_x)
            edge_arrow_source.data['end_y'].append(end_y)
            edge_arrow_source.data['color'].append(FINAL_TRACE_EDGE_COLOR if in_final_trace else OTHER_EDGE_COLOR)

    # Add the label
    edge_label_source.data['from'].append(edge.from_node)
    edge_label_source.data['to'].append(edge.to_node)
    edge_label_source.data['x'].append((start_x + end_x) / 2)
    edge_label_source.data['y'].append((start_y + end_y) / 2)
    edge_label_source.data['label'].append(edge.label)


def _add_self_loop_to_sources(nodes: list[Node], edge: Edge, in_final_trace: bool, edge_arrow_source: ColumnDataSource,
                              edge_bezier_source: ColumnDataSource, edge_label_source: ColumnDataSource):
    """
    Add a self-loop edge for a node to the ColumnDataSources, consisting of a Beziér curve and an arrow.
    """
    connection = _get_connection_coordinates(nodes, edge.from_node)

    right_x, right_y = connection[1]

    # Add the Bézier curve
    edge_bezier_source.data['from'].append(edge.from_node)
    edge_bezier_source.data['to'].append(edge.to_node)
    edge_bezier_source.data['start_x'].append(right_x)
    edge_bezier_source.data['start_y'].append(right_y + 5)
    edge_bezier_source.data['end_x'].append(right_x)
    edge_bezier_source.data['end_y'].append(right_y - 5)
    edge_bezier_source.data['control1_x'].append(right_x + 25)
    edge_bezier_source.data['control1_y'].append(right_y + 25)
    edge_bezier_source.data['control2_x'].append(right_x + 25)
    edge_bezier_source.data['control2_y'].append(right_y - 25)
    edge_bezier_source.data['color'].append(FINAL_TRACE_EDGE_COLOR if in_final_trace else OTHER_EDGE_COLOR)

    # Add the arrow
    edge_arrow_source.data['from'].append(edge.from_node)
    edge_arrow_source.data['to'].append(edge.to_node)
    edge_arrow_source.data['start_x'].append(right_x + 0.001)
    edge_arrow_source.data['start_y'].append(right_y - 5.001)
    edge_arrow_source.data['end_x'].append(right_x)
    edge_arrow_source.data['end_y'].append(right_y - 5)
    edge_arrow_source.data['color'].append(FINAL_TRACE_EDGE_COLOR if in_final_trace else OTHER_EDGE_COLOR)

    # Add the label
    edge_label_source.data['from'].append(edge.from_node)
    edge_label_source.data['to'].append(edge.to_node)
    edge_label_source.data['x'].append(right_x + 25)
    edge_label_source.data['y'].append(right_y)
    edge_label_source.data['label'].append(edge.label)


def _add_node_to_sources(node: Node, final_trace: list[str], node_source: ColumnDataSource,
                         node_label_source: ColumnDataSource):
    """
    Add a node to the ColumnDataSources.
    """
    node_source.data['id'].append(node.node_id)
    node_source.data['x'].append(node.x)
    node_source.data['y'].append(node.y)
    node_source.data['w'].append(node.width)
    node_source.data['h'].append(node.height)
    node_source.data['color'].append(
        FINAL_TRACE_NODE_COLOR if node.node_id in final_trace else OTHER_NODE_COLOR)

    node_label_source.data['id'].append(node.node_id)
    node_label_source.data['x'].append(node.x - node.width / 2 + HORIZONTAL_PADDING_WITHIN_NODES)
    node_label_source.data['y'].append(node.y)
    node_label_source.data['label'].append(node.label)

def _calculate_dimensions(label: str) -> tuple[float, float]:
    """
    Calculate a node's dimensions based on its label and the given font size constant.
    Assumes the font is Courier New.
    """
    lines = label.splitlines()
    width = 0
    for line in lines:
        width = max(width, len(line) * (MAJOR_FONT_SIZE / 3 + 5))
    height = len(lines) * (MAJOR_FONT_SIZE / 2 + 9) * 1.37 - 9
    return width + 2 * HORIZONTAL_PADDING_WITHIN_NODES, height + 2 * VERTICAL_PADDING_WITHIN_NODES


def _flip_edges(edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Calculate which edges need to be flipped to make a graph acyclic.
    """
    # Step 1: Build adjacency list from edges
    adj = {}
    for u, v in edges:
        if u not in adj:
            adj[u] = []
        adj[u].append(v)

    # Step 2: Helper function to detect cycles
    def dfs(node, visited, rec_stack, cycle_edges):
        visited[node] = True
        rec_stack[node] = True

        if node in adj:
            for neighbor in adj[node]:
                edge = (node, neighbor)

                if not visited.get(neighbor, False):
                    if dfs(neighbor, visited, rec_stack, cycle_edges):
                        cycle_edges.append(edge)
                elif rec_stack.get(neighbor, False):
                    # Found a cycle, add the edge to the cycle_edges list
                    cycle_edges.append(edge)

        rec_stack[node] = False
        return False

    # Step 3: Detect cycles
    visited = {}
    rec_stack = {}
    cycle_edges = []

    for node in adj:
        if not visited.get(node, False):
            dfs(node, visited, rec_stack, cycle_edges)

    # Step 4: Return the list of edges that need to be flipped
    # In this case, the cycle_edges are the ones that we need to "break" by flipping
    return cycle_edges
