import random
import string

from robot.api.deco import keyword  # type:ignore
from robotmbt.modelspace import ModelSpace
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.graphs.scenariograph import ScenarioGraph
from robotmbt.visualise.graphs.abstractgraph import AbstractGraph
from robotmbt.visualise.graphs.stategraph import StateGraph


class ModelGenerator:
    @keyword(name="Create Graph") # type: ignore
    def create_graph(self, graph_type :str) -> AbstractGraph:
        match graph_type:
            case "scenario":
                return ScenarioGraph()
            case "state":
                return StateGraph()
            case _:
                raise Exception(f"Trying to create unknown graph type {graph_type}")


    @keyword(name="Generate Trace Information")  # type: ignore
    def generate_trace_info(self, scenario_count: int) -> TraceInfo:
        """Generates a list of unique random scenarios."""
        scenarios: list[ScenarioInfo] = ModelGenerator.generate_scenario_names(
            scenario_count)

        return TraceInfo(scenarios, StateInfo(ModelSpace()))

    @keyword(name="Ensure Scenario Present")  # type: ignore
    def ensure_scenario_present(self, trace_info: TraceInfo, scenario_name: str) -> TraceInfo:
        if trace_info.contains_scenario(scenario_name):
            return trace_info

        trace_info.add_scenario(ScenarioInfo(scenario_name))
        return trace_info

    @keyword(name="Ensure Scenario Follows")  # type: ignore
    def ensure_scenario_follows(self, trace_info: TraceInfo, scen1: str, scen2: str) -> TraceInfo:
        scen1_info: ScenarioInfo | None = trace_info.get_scenario(scen1)
        scen2_info: ScenarioInfo | None = trace_info.get_scenario(scen2)

        if scen1_info is None or scen2_info is None:
            raise Exception(
                f"Ensure Scenario Follows for scenarios that did not exist! scen1={scen1}, scen2={scen2}")

        # both scenarios apparently exist, now make sure that scenario2 follows after some appearance of scenario 1:
        scen1_index: int = trace_info.trace.index(scen1_info)
        scen2_index: int = trace_info.trace.index(scen2_info)
        if scen2_index == scen1_index + 1:
            return trace_info

        # if it doesn't follow, make it follow
        trace_info.insert_trace_at(scen1_index, scen2_info)
        return trace_info

    @keyword(name="Ensure Edge Exists")  # type: ignore
    def ensure_edge_exists(self, graph: ScenarioGraph, scen_name1: str, scen_name2: str):
        # get node name based on scenario
        nodename1: str = ""
        nodename2: str = ""
        for (nodename, label) in graph.networkx.nodes(data='label', default=None):
            if label == scen_name1:
                nodename1 = nodename

            if label == scen_name2:
                nodename2 = nodename

        # now check the relation:
        if (nodename1, nodename2) in graph.networkx.edges:  # type: ignore
            return  # exists :)

        # make sure that it exists
        graph.networkx.add_edge(nodename1, nodename2)

    @staticmethod
    def generate_random_scenario_name(length: int = 10) -> str:
        """Generates a random scenario name."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_scenario_names(count: int) -> list[ScenarioInfo]:
        """Generates a list of unique random scenarios."""
        scenarios: set[str] = set()
        while len(scenarios) < count:
            scenario = ModelGenerator.generate_random_scenario_name()
            scenarios.add(scenario)
        return [ScenarioInfo(s) for s in scenarios]
