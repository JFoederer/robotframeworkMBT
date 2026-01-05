from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import StateInfo, ScenarioInfo
from robotmbt.modelspace import ModelSpace


class DeltaValueGraph(AbstractGraph[set[tuple[str, str]], ScenarioInfo]):
    """
    The state graph is a more advanced representation of trace exploration, allowing you to see the internal state.
    It represents states as nodes, and scenarios as edges.
    """

    @staticmethod
    def select_node_info(pairs: list[tuple[ScenarioInfo, StateInfo]], index: int) -> set[tuple[str, str]]:
        if index == 0:
            return StateInfo(ModelSpace()).difference(pairs[0][1])
        else:
            return pairs[index-1][1].difference(pairs[index][1])

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> ScenarioInfo:
        return pair[0]

    @staticmethod
    def create_node_label(info: set[tuple[str, str]]) -> str:
        res = ""
        for assignment in info:
            res += "\n"+assignment[0]+":"+assignment[1]
        return f"{res}"

    @staticmethod
    def create_edge_label(info: ScenarioInfo) -> str:
        return info.name

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Execution State Update (in final trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Execution State Update (backtracked)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "Executed Scenario (in final trace)"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "Executed Scenario (backtracked)"
