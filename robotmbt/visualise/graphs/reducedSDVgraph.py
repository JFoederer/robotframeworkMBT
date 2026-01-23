import networkx

from robotmbt.modelspace import ModelSpace
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo, TraceInfo


class ReducedSDVGraph(AbstractGraph[tuple[ScenarioInfo, set[tuple[str, str]]], None]):
    """
    The reduced Scenario-delta-Value graph keeps track of both the scenarios and state updates encountered.
    It is produced by taking the Scenario-delta-Value graph and merging nodes that have the same Scenario associated,
    an edge between them and the same incoming/outgoing edges except for at most one incoming or outgoing edge per node.
    Visually: ... -> node0 -> node1 -> node2 -> ...
    get merged (if they have the same scenario's and incoming/outgoing edges that are not visually represented)
    """

    def chain_equiv(self, node1, node2) -> bool:
        context = self.networkx
        if not node1 == 'start' and not node2 == 'start' and self.ids[node1][0] == self.ids[node2][0] and \
                (networkx.has_path(context, node1, node2) or networkx.has_path(context, node2, node1)):
            return len(set(context.in_edges(node1)) ^ set(context.in_edges(node2))) <= 2 and \
                len(set(context.out_edges(node1)) ^ set(context.out_edges(node2))) <= 2
        else:
            return False

    @staticmethod
    def _generate_equiv_class_label(equiv_class, old_labels):
        if len(equiv_class) == 1:
            return old_labels[set(equiv_class).pop()]
        else:
            return "(merged: " + str(len(equiv_class)) + ")\n" + old_labels[set(equiv_class).pop()]

    def __init__(self, info: TraceInfo):
        super().__init__(info)
        old_labels = networkx.get_node_attributes(self.networkx, "label")
        self.networkx = networkx.quotient_graph(self.networkx, lambda x, y: self.chain_equiv(x, y),
                                                node_data=lambda equiv_class: {
                                                    'label': self._generate_equiv_class_label(equiv_class, old_labels)},
                                                edge_data=lambda x, y: {'label': ''})
        # TODO make generated label more obvious to be equivalence class
        nodes = self.networkx.nodes

        new_networkx: networkx.DiGraph = networkx.DiGraph()

        for node_id in self.networkx.nodes:
            new_id: tuple[str, ...] = tuple(sorted(node_id))
            new_networkx.add_node(new_id)
            new_networkx.nodes[new_id]['label'] = self.networkx.nodes[node_id]['label']

        for (from_id, to_id) in self.networkx.edges:
            new_from_id: tuple[str, ...] = tuple(sorted(from_id))
            new_to_id: tuple[str, ...] = tuple(sorted(to_id))
            new_networkx.add_edge(new_from_id, new_to_id)
            new_networkx.edges[(new_from_id, new_to_id)]['label'] = self.networkx.edges[(from_id, to_id)]['label']

        for i in range(len(self.final_trace)):
            current_node = self.final_trace[i]
            for new_node in nodes:
                if current_node in new_node:
                    self.final_trace[i] = tuple(sorted(new_node))

        self.networkx = new_networkx
        self.start_node: tuple[str, ...] = tuple(['start'])

    @staticmethod
    def select_node_info(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) \
            -> tuple[ScenarioInfo, set[tuple[str, str]]]:
        if index == 0:
            return trace[0][0], StateInfo(ModelSpace()).difference(trace[0][1])
        else:
            return trace[index][0], trace[index - 1][1].difference(trace[index][1])

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_description(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> str:
        return str(trace[index][1]).replace('\n', '<br>')

    @staticmethod
    def create_node_label(info: tuple[ScenarioInfo, set[tuple[str, str]]]) -> str:
        return ScenarioDeltaValueGraph.create_node_label(info)

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Executed Scenario w/ Changes in Execution State (in final trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Executed Scenario w/ Changes in Execution State (backtracked)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "Execution Flow (final trace)"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "Execution Flow (backtracked)"

    @staticmethod
    def get_tooltip_name() -> str:
        return "Full state"
