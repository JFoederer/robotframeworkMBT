import jsonpickle  # type: ignore
from robot.api.deco import keyword  # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.visualiser import Visualiser
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
import os
import networkx as nx
from robotmbt.visualise.networkvisualiser import NetworkVisualiser, Node


class ModelGenerator:
    @keyword(name='Generate Trace Information')  # type:ignore
    def generate_trace_information(self) -> TraceInfo:
        return TraceInfo()

    @keyword(name='The Algorithm Inserts')  # type:ignore
    def insert_trace_info(self, trace_info: TraceInfo, scenario_name: str, state_str: str | None = None) -> TraceInfo:
        '''
        State should be of format
        "name: key=value key2=value2 ..."
        '''

        (scen_info, state_info) = self.__convert_to_info_tuple(scenario_name, state_str)
        trace_info.update_trace(scen_info, state_info, trace_info.previous_length+1)

        return trace_info

    @keyword(name='All Traces Contains List')  # type:ignore
    def all_traces_contains_list(self, trace_info: TraceInfo) -> TraceInfo:
        trace_info.all_traces.append([])
        return trace_info

    @keyword(name='All Traces Contains')  # type:ignore
    def all_traces_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str | None) -> TraceInfo:
        '''
        State should be of format
        "scenario: key=value"
        '''
        (scen_info, state_info) = self.__convert_to_info_tuple(scenario_name, state_str)

        for trace in trace_info.all_traces:
            trace.append((scen_info, state_info))

        return trace_info

    @keyword(name='Generate Graph')  # type:ignore
    def generate_graph(self, trace_info: TraceInfo, graph_type: str) -> AbstractGraph:
        return Visualiser(graph_type=graph_type, trace_info=trace_info)._get_graph()

    @keyword(name="Generate Network Graph")
    def generate_networkgraph(self, graph: AbstractGraph) -> NetworkVisualiser:
        return NetworkVisualiser(graph=graph, suite_name="", seed="")

    @keyword(name='Export Graph')  # type:ignore
    def export_graph(self, suite: str, trace_info: TraceInfo) -> str:
        return trace_info.export_graph(suite, True)

    @keyword(name='Import Graph')  # type:ignore
    def import_graph(self, filepath: str) -> TraceInfo:
        with open(filepath, 'r') as f:
            string = f.read()
            decoded_instance: TraceInfo = jsonpickle.decode(string)  # type: ignore
        visualiser = Visualiser('state', trace_info=decoded_instance)
        return visualiser.trace_info

    @keyword(name='Check File Exists')  # type:ignore
    def check_file_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath)

    @keyword(name='Compare Trace Info')  # type:ignore
    def compare_trace_info(self, t1: TraceInfo, t2: TraceInfo) -> bool:
        return repr(t1) == repr(t2)

    @keyword(name='Delete File')  # type:ignore
    def delete_file(self, filepath: str):
        os.remove(filepath)

    @keyword(name='Graph Contains Vertex With No Text')  # type:ignore
    def graph_contains_no_text(self, graph: AbstractGraph, label: str) -> bool:
        return label in graph.networkx.nodes()

    @keyword(name='Graph Contains Vertex With Text')  # type:ignore
    def graph_contains_vertex_with_text(self, graph: AbstractGraph, title: str, text: str | None = None) -> str | None:
        """
        Returns the label of the complete node or None if it doesn't exist
        """
        ATTRIBUTE = "label"
        attr = nx.get_node_attributes(graph.networkx, ATTRIBUTE)

        (_, state_info) = self.__convert_to_info_tuple(title, text)
        parts = state_info.properties[text.split(":")[0]] \
            if text is not None else []

        for nodename, label in attr.items():
            if title in label:
                if text is None:
                    # we sanitise because newlines in text go badly with eval() in Robot framework
                    return nodename

                count = 0
                for s in parts:
                    if f"{s}={parts[s]}" in label:
                        count += 1
                if count == len(parts):
                    # we sanitise because newlines in text go badly with eval() in Robot framework
                    return nodename

        return None

    @keyword(name="Vertices Are Connected")  # type:ignore
    def vertices_connected(self, graph: AbstractGraph, node_key1: str | None, node_key2: str | None) -> bool:
        if node_key1 is None or node_key2 is None:
            return False
        return graph.networkx.has_edge(node_key1, node_key2)
    
    @keyword(name="Get NodeID")  # type:ignore
    def get_nodeid(self, graph: AbstractGraph, node_title:str) -> str | None:
        return self.graph_contains_vertex_with_text(graph, node_title, text=None)

    @keyword(name="Get Vertex Y Position")  # type:ignore
    def get_y(self, network_vis: NetworkVisualiser, id: str) -> int | None:
        try:
            node: Node | None = network_vis.node_dict[id]
            return node.y
        except KeyError:
            return None

    @keyword(name='Graph Contains Vertices Starting With')  # type:ignore
    def scen_graph_contains_vertices_starting_with(self, graph: AbstractGraph, vertices_str: str) -> bool | str:
        '''
        vertices_str should be of format "'vertex1', 'vertex2'" etc
        '''
        attr: dict[str, str] = nx.get_node_attributes(graph.networkx, "label")

        vertices = vertices_str.split("'")
        for i in range(1, len(vertices), 2):
            found = False
            for _, label in attr.items():
                if label.startswith(vertices[i]):
                    found = True
                    break

            if not found:
                return False

        return True

    @keyword(name='Backtrack')  # type:ignore
    def backtrack(self, trace_info: TraceInfo, steps: int) -> TraceInfo:
        scenario, state = trace_info.current_trace[-steps - 1]
        trace_info.update_trace(scenario, state, len(trace_info.current_trace) - steps)
        return trace_info

    @keyword(name='Get Length Current Trace')  # type:ignore
    def get_length_current_trace(self, trace_info: TraceInfo) -> int:
        return len(trace_info.current_trace)

    @keyword(name='Get Number of Backtracked Traces')  # type:ignore
    def get_number_of_backtracked_traces(self, trace_info: TraceInfo) -> int:
        return len(trace_info.all_traces)

    # ============= #
    # == HELPERS == #
    # ============= #

    @staticmethod
    def __convert_to_info_tuple(scenario_name: str, keyvaluestr: str | None) -> tuple[ScenarioInfo, StateInfo]:
        """
        Format:
        "domain1: key1=value1, key2=value2"
        """
        scenario_name = scenario_name.strip()
        if keyvaluestr is None:
            return (ScenarioInfo(scenario_name), StateInfo._create_state_with_prop("", []))

        keyvaluestr = keyvaluestr.strip()

        split_domain: list[str] = keyvaluestr.split(':')
        domain = split_domain[0]
        keyvaluestr = ":".join(split_domain[1:]) if len(split_domain) > 2 else split_domain[1]

        # contains ["key1", "value1 key2", "value2"]-like structure
        split_eq: list[str] = keyvaluestr.split("=")
        if len(split_eq) < 2:
            raise ValueError(
                "Please input a valid state information string of format \"scenario1: key1=value1 key2=value2\""
            )

        keyvalues: list[tuple[str, str]] = []

        prev_key = split_eq[0]
        for index in range(1, len(split_eq)):
            splits: list[str] = ModelGenerator.__split_top_level(split_eq[index])
            splits = [s.strip() for s in splits]
            prev_value: str = " ".join(splits[:-1]) if len(splits) > 1 else splits[0]
            new_key: str = splits[-1]

            keyvalues.append((prev_key, prev_value))
            prev_key = new_key

        return (ScenarioInfo(scenario_name), StateInfo._create_state_with_prop(domain, keyvalues))

    @staticmethod
    def __split_top_level(text):
        parts = []
        buf = []

        depth = 0
        string_char = None
        escape = False

        i = 0
        n = len(text)

        while i < n:
            ch = text[i]

            # Inside string
            if string_char:
                buf.append(ch)
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == string_char:
                    string_char = None
                i += 1
                continue

            # Start of string
            if ch in ("'", '"'):
                string_char = ch
                buf.append(ch)
                i += 1
                continue

            # Nesting
            if ch in "([{":
                depth += 1
                buf.append(ch)
                i += 1
                continue

            if ch in ")]}":
                depth -= 1
                buf.append(ch)
                i += 1
                continue

            # Split condition: ", " at top level
            if ch == "," and i + 1 < n and text[i + 1] == " " and depth == 0:
                parts.append("".join(buf))
                buf.clear()
                i += 2  # skip ", "
                continue

            buf.append(ch)
            i += 1

        parts.append("".join(buf))
        return parts
