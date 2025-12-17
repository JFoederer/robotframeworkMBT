from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import StateInfo, ScenarioInfo


class StateGraph(AbstractGraph[StateInfo, ScenarioInfo]):
    """
    The state graph is a more advanced representation of trace exploration, allowing you to see the internal state.
    It represents states as nodes, and scenarios as edges.
    """

    @staticmethod
    def select_node_info(pairs: list[tuple[ScenarioInfo, StateInfo]], index: int) -> StateInfo:
        return pairs[index][1]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo:
        return pair[0]

    @staticmethod
    def create_node_label(info: StateInfo) -> str:
        return str(info)

    @staticmethod
    def create_edge_label(info: ScenarioInfo) -> str:
        return info.name
