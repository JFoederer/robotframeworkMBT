from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo


class ScenarioStateGraph(AbstractGraph[tuple[ScenarioInfo, StateInfo], None]):
    """
    The scenario-State graph keeps track of both the scenarios and states encountered.
    Its nodes are scenarios together with the state after the scenario has run.
    Its edges represent steps in the trace.
    """

    @staticmethod
    def select_node_info(pairs: list[tuple[ScenarioInfo, StateInfo]], index: int) -> tuple[ScenarioInfo, StateInfo]:
        return pairs[index]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_label(info: tuple[ScenarioInfo, StateInfo]) -> str:
        return f"{info[0].name}\n\n{str(info[1])}"

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Executed Scenario w/ Execution State (in final trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Executed Scenario w/ Execution State (backtracked)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "Execution Flow (final trace)"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "Execution Flow (backtracked)"
