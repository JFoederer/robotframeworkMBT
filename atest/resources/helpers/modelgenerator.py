import random
import string

from robot.api.deco import keyword # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, ModelSpace

class ModelGenerator:    
    @keyword(name="Generate Trace Information") # type: ignore
    def generate_trace_info(self, scenario_count :int) -> TraceInfo:
        """Generates a list of unique random scenarios."""
        scenarios :list[ScenarioInfo] = ModelGenerator.generate_scenario_names(scenario_count)

        return TraceInfo(scenarios, ModelSpace())

    @staticmethod
    def generate_random_scenario_name(length :int=10) -> str:
        """Generates a random scenario name."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_scenario_names(count :int) -> list[ScenarioInfo]:
        """Generates a list of unique random scenarios."""
        scenarios :set[str] = set()
        while len(scenarios) < count:
            scenario = ModelGenerator.generate_random_scenario_name()
            scenarios.add(scenario)
        return [ScenarioInfo(s) for s in scenarios]
