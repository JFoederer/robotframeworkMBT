# Contribution guidelines RobotMBT

Welcome! Thank you for considering to contribute to this project. If you haven't already, because your contribution already starts when you use this software and share your experiences with the people around you. These guidelines will help you to further connect with the online community.

## Communication channels

### Slack

If you want to ask or answer questions and participate in discussions, then the [Robot Framework Slack](http://slack.robotframework.org/) channels are a good place to do so.

### GitHub

If you want to get involved on GitHub, you can so by submitting issues or offering code improvements. These guidelines will help you to find your way. These guidelines expect readers to have a basic knowledge about open source as well as why and how to contribute to an open source project. If you are new to these topics, please have a look at the generic [Open Source Guides](https://opensource.guide/) first.

## Code of Conduct

If you want to be part of this community, then we expect you to respect our norms and values. These are in line with the [GitHub Code of Conduct](https://docs.github.com/en/site-policy/github-terms/github-community-code-of-conduct) and the [Slack Code of Conduct](https://docs.slack.dev/community-code-of-conduct/). In short, we expect you to:

- Be welcoming.
- Be kind.
- Look out for each other.

## Submitting issues

Defects and enhancements are tracked in [GitHub Issues](https://github.com/JFoederer/robotframeworkMBT/issues). Before submitting an issue here, please make sure the issue is caused by this project in particular. If you are unsure if something is worth submitting, you can first ask on [Slack](http://slack.robotframework.org/). Before submitting a new issue, it is always a good idea to check if something similar was already reported. If it is, please add your comments to the existing issue instead of creating a new one. Communication in issues on GitHub is done in English.

Take notice that issues do not get resolved by themselves. Someone will need to spend time on the topic. Be prepared to wait, contribute yourself or arrange budget to hire someone for the job.

### Reporting defects

When reporting a defect, be precise and concise in your description. Write in way that helps others understand and reproduce the issue. Screenshots can be very helpful, but when adding logging or other textual information, please keep the textual form.

Note that all information in the issue tracker is public. *Do not include any confidential information there*.

Be sure to add information about:

- The applicable version(s) of RobotMBT (use `pip list` and check for `robotframework-mbt`)
- Your Robot Framework version (use `pip list` and check for `robotframework`)
- Your Python version (check using `python --version`)
- Your operating system
- Your custom settings for RobotMBT (at the library and test suite level)

Version information about Robot Framework, Python and the operating system are also reported at the start of Robot's `output.xml` file.

### Enhancement requests

When proposing an enhancement, a feature request, be clear about the use cases. Who will benefit from the enhancement and in what way? Describe the expected behaviour and use concrete examples to illustrate the intent.

## Code contributions

If you have fixed a defect or implemented an enhancement, you can contribute your changes via a [GitHub Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). This is not restricted to implementation code: on the contrary, fixes and enhancements to documentation and tests alone are also very valuable!

### First steps

- [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) and/or [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks) the RobotMBT repo. If you are not a fan of command line tools, [GitHub Desktop](https://github.com/apps/desktop) can help you.
- [Run the tests](#running-tests) to check your starting point.
- Write new failing tests to cover your intended changes.
- Implement your changes.
- Verify that your tests pass with your implementation.

### Definition of Done

The Definition of Done for RobotMBT is when a pull request is merged. This is to ensure that pull requests are fully self-contained, and leave no open ends. 

In other words: when the pull request is merged, it is 100% done. This keeps the main branch ready for release at all times.

This means that for each pull request you need to ensure that:

- [No regression](#non-regression-criteria) is introduced.
- New functionality is covered by [tests](#guidelines-for-writing-new-tests).
- [Code style](#code-style) follows the standard.
- Documentation is up to date.
- The PR branch is 0 commits behind the main branch.

### Running tests

Tests can be executed from the command line by running `python run_tests.py`. This will run all unit tests, followed by the Robot acceptance tests. Use `--help` for additional info.

### Non-regression criteria

The criteria for proving non-regression are:

- All automated regression tests pass
- All supported Python, Robot Framework and OS versions still work (see `pyproject.toml` for supported versions).
- The [demo](https://github.com/JFoederer/robotframeworkMBT/tree/main/demo/Titanic) still works.
- Manual checks are executed to cover the automation's blind spots and subjective elements (e.g. some visual inspection on layout and assessing overall look and feel).

### Guidelines for writing new tests

For this project, we are not maintaining separate requirements documentation. The user documentation explains the software's purpose and scope, while tests further specify its concrete behaviour. Keep this in mind when writing tests and pay extra attention to documenting your test cases: they are more than just bug catchers. If code exists due to a technical limitation rather than a requirement, be sure to document your design decision.

Tests are located in the `atest` and `utest` folders, which stands for _acceptance test_ and _unit test_ respectively. The acceptance tests are Robot tests that cover user-visible behaviour using black-box testing techniques. They typically do not cover all details, unless some Robot Framework interaction is involved. The unit tests go more in-depth, including white box techniques to cover the _dark corners_ of the code. Choose the right type of test for what you are covering.

A specific challenge for this project is that there is a lot of test case generation going on. Be wary that variations in the generation process do not alter the intended coverage of a test and do not yield false positives (passing results without proof for passing), such as checking "_all_" results in an empty list. Lastly: keep the resulting total number of test cases in a run deterministic. This allows for a quick check that all test cases are still being generated.

### Code style

Maintainability is the main driver for coding style. Always write your code with the mindset that you are writing it for someone else, and that this person's experience level is slightly below the average in the project. Code is written following the [PEP 8](https://peps.python.org/pep-0008) Style guide and [SOLID](https://en.wikipedia.org/wiki/SOLID) principles.

#### Formatting

Formatting follows the default rules of [autopep8](https://pypi.org/project/autopep8/) with the exception of the maximum line length (see https://github.com/JFoederer/robotframeworkMBT/tree/main/.github/workflows/autopep8.yml). Note however, that the extended line length is not an invite to always write long lines.

Researchers have suggested that longer lines are better suited for cases when the information will likely be scanned, while shorter lines (45-75 characters) are appropriate when the information is meant to be read thoroughly [[ref.](https://www.academia.edu/6232736/The_influence_of_font_type_and_line_length_on_visual_search_and_information_retrieval_in_web_pages)]. Keep this in mind when writing code and documentation, taking the current indentation level into account.

#### Docstrings, comments and logging

- Docstrings are written using a black-box approach. One should not need to know the inside of a class or function in order to use it.
- Use comments to annotate code for maintainers.
- Prevent trivial comments and use descriptive names to make your code self-explanatory.
- When documenting external interfaces, also check whether the user documentation requires an update.
- Log useful information that is runtime-dependent.
  - Information that is useful after a passing test run is logged at info-level.
  - Information that is useful for analysing failed tests is logged at debug-level.

- Be careful not to make assumptions in what you log: Recheck log statements if your changes affect the context in which the code is run, and only report about what you know to be true.

### Creating new graphs

Extending the functionality of the visualizer with new graph types can result in better insights into created tests. The visualizer makes use of an abstract graph class that makes it easy to create new graph types.

To create a new graph type, create an instance of AbstractGraph, instantiating the following methods:
- select_node_info: select the information you want to use to identify different nodes from all ScenarioInfo/StateInfo pairs that make up the different exploration steps. This info is also used to label nodes. Its return type has to match the first type used to instantiate AbstractGraph.
- select_edge_info: ditto but for edges, which is also used for labeling. Its type has to match the second type used to instantiate AbstractGraph.
- create_node_label: turn the selected information into a label for a node.
- create_edge_label: ditto but for edges.
- get_legend_info_final_trace_node: return the text you want to appear in the legend for nodes that appear in the final trace.
- get_legend_info_other_node: ditto but for nodes that have been backtracked.
- get_legend_info_final_trace_edge: ditto but for edges that appear in the final trace.
- get_legend_info_other_edge: ditto but for edges that have backtracked.

It is recommended to create a new file for each graph type under `/robotmbt/visualise/graphs/`.

A simple example is given below. In this graph type, nodes represent scenarios encountered in exploration, and edges show the flow between these scenarios.

```python
class ScenarioGraph(AbstractGraph[ScenarioInfo, None]):
    @staticmethod
    def select_node_info(pairs: list[tuple[ScenarioInfo, StateInfo]], index: int) -> ScenarioInfo:
        return pairs[index][0]

    @staticmethod
    def select_edge_info(pair: tuple[ScenarioInfo, StateInfo]) -> None:
        return None
 
    @staticmethod
    def create_node_label(info: ScenarioInfo) -> str:
        return info.name

    @staticmethod
    def create_edge_label(info: None) -> str:
        return ''

    @staticmethod
    def get_legend_info_final_trace_node() -> str:
        return "Executed Scenario (in final trace)"

    @staticmethod
    def get_legend_info_other_node() -> str:
        return "Executed Scenario (backtracked)"

    @staticmethod
    def get_legend_info_final_trace_edge() -> str:
        return "Execution Flow (final trace)"

    @staticmethod
    def get_legend_info_other_edge() -> str:
        return "Execution Flow (backtracked)"
```

Once you have created a new Graph class, you can direct the visualizer to use it when your type is selected. 
Edit `/robotmbt/visualise/visualiser.py` to not reject your graph type in `__init__` and construct your graph in `generate_visualisation` like the others. For our example:
```python
def __init__(self, graph_type: str, suite_name: str = "", seed: str = "", export: bool = False, trace_info: TraceInfo = None):
        if graph_type != 'scenario' and [...]:
            raise ValueError(f"Unknown graph type: {graph_type}!")

        [...]
```

```python
def generate_visualisation(self) -> str:
    [...]

    if self.graph_type == 'scenario':
        graph: AbstractGraph = ScenarioGraph(self.trace_info)

    [...]
```

Now, when selecting your graph type (in our example `Treat this test suite Model-based  graph=scenario`), your graph will get constructed!

