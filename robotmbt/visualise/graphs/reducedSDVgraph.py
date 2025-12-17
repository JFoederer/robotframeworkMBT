import networkx

from robotmbt.modelspace import ModelSpace
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.scenariodeltavaluegraph import ScenarioDeltaValueGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo, TraceInfo


# TODO add tests for this graph representation
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

    def __init__(self, info: TraceInfo):
        super().__init__(info)
        old_labels = networkx.get_node_attributes(self.networkx, "label")
        self.networkx = networkx.quotient_graph(self.networkx, lambda x, y: self.chain_equiv(x, y),
                                                node_data=lambda equiv_class: {
                                                    'label': old_labels[set(equiv_class).pop()]},
                                                edge_data=lambda x, y: {'label': ''})
        # TODO make generated label more obvious to be equivalence class
        nodes = self.networkx.nodes
        for i in range(len(self.final_trace)):
            current_node = self.final_trace[i]
            for new_node in nodes:
                if current_node in new_node:
                    self.final_trace[i] = new_node

    @staticmethod
    def select_node_info(pairs: list[tuple[ScenarioInfo, StateInfo]], index: int) \
            -> tuple[ScenarioInfo, set[tuple[str, str]]]:
        if index == 0:
            return pairs[0][0], StateInfo(ModelSpace()).difference(pairs[0][1])
        else:
            return pairs[index][0], pairs[index - 1][1].difference(pairs[index][1])

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_label(info: tuple[ScenarioInfo, set[tuple[str, str]]]) -> str:
        return f"{info[0].name}\n{ScenarioDeltaValueGraph.assignment_rep(info[1])}"

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''
