# How to: Creating new graphs

Extending the functionality of the visualiser with new graph types can result in better insights into created tests. The visualiser makes use of an abstract graph class that makes it easy to create new graph types.

To create a new graph type, create an instance of `robotmbt/visualise/graphs/AbstractGraph`, instantiating the abstract methods. Please place the graph under `robotmbt/visualise/graphs/`.

**NOTE**: when manually altering the `networkx` field, ensure its IDs remain as a serializable and hashable type when the constructor finishes.

As an example, we show the implementation of the scenario graph below. In this graph type, nodes represent scenarios encountered in exploration, and edges show the flow between these scenarios.
It does not enable tooltips.

```python
class ScenarioGraph(AbstractGraph[ScenarioInfo, None]):
    @staticmethod
    def select_node_info(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> ScenarioInfo:
        return trace[index][0]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None

    @staticmethod
    def create_node_description(trace: list[tuple[ScenarioInfo, StateInfo]], index: int) -> str:
        return ''

    @staticmethod
    def create_node_label(info: ScenarioInfo) -> str:
        return info.name

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Scenario (part of trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Scenario (not in trace)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "path included in trace"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "not selected for trace"

    @staticmethod
    def get_tooltip_name() -> str:
        return ""
```

Once you have created a new Graph class, you can direct the visualiser to use it when your type is selected. 
Simply add your class to the `GRAPHS` dictionary in `robotmbt/visualise/visualiser.py` like the others. For our example:

```python
GRAPHS = {
    ...
    'scenario': ScenarioGraph,
    ...
}
```

Now, when selecting your graph type (in our example `Treat this test suite Model-based    graph=scenario`), your graph will get constructed!

**NOTE**: You need the optional dependencies for visualisation to create graphs, e.g.:

```bash
pip install .[visualisation]
```

**TIP**: [Python virtual environments](https://docs.python.org/3/library/venv.html) are an easy way to test with different Python version and sets of dependencies.
