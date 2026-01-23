from robotmbt.modelspace import ModelSpace

from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo


class ScenarioDeltaValueGraph(AbstractGraph[tuple[ScenarioInfo, set[tuple[str, str]]], None]):
    """
    The Scenario-delta-Value graph keeps track of both the scenarios and state updates encountered.
    Its nodes are scenarios together with the property assignments after the scenario has run.
    Its edges represent steps in the trace.
    """

    @staticmethod
    def select_node_info(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) \
            -> tuple[ScenarioInfo, set[tuple[str, str]]]:
        if index == 0:
            return trace[0][0], StateInfo(ModelSpace()).difference(trace[0][1])
        else:
            return trace[index][0], trace[index-1][1].difference(trace[index][1])

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_description(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> str:
        return str(trace[index][1]).replace('\n', '<br>')

    @staticmethod
    def create_node_label(info: tuple[ScenarioInfo, set[tuple[str, str]]]) -> str:
        res = ""
        for assignment in info[1]:
            res += "\n\n"+assignment[0]+":"+assignment[1]
        return f"{info[0].name}{res}"

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
