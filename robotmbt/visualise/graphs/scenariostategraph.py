from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.models import ScenarioInfo, StateInfo


class ScenarioStateGraph(AbstractGraph[tuple[ScenarioInfo, StateInfo], None]):
    """
    The scenario-State graph keeps track of both the scenarios and states encountered.
    Its nodes are scenarios together with the state after the scenario has run.
    Its edges represent steps in the trace.
    """

    @staticmethod
    def select_node_info(pair: tuple[ScenarioInfo, StateInfo]) -> tuple[ScenarioInfo, StateInfo]:
        return pair

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_label(info: tuple[ScenarioInfo, StateInfo]) -> str:
        return f"{info[0].name}\n\n{str(info[1])}"

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''
