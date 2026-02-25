*** Settings ***
Documentation     This suite takes the graph generated earlier in the visualisation suite
...               and uses it to check import functionality.
Library           robotmbt
Library           graph_checker.py
Library           Collections

*** Variables ***
${prior_export}    ${OUTPUT_DIR}${/}run_model_with_graph.json

*** Test Cases ***
Import as any graph type
    [Documentation]    The data that is stored during export is always the compelte data set. This
    ...                has the advantage that different graph types can be reconstructed from the
    ...                data without rerunning the model.
    Import graph data from    ${prior_export}    graph_type=scenario
    Show model graph from exported file    ${prior_export}    graph_style=scenario
    ${node_count}=    Number of graph nodes
    Should be equal    ${node_count}    ${4}
    Import graph data from    ${prior_export}    graph_type=scenario-delta-value
    Show model graph from exported file    ${prior_export}    graph_style=scenario-delta-value
    ${node_count}=    Number of graph nodes
    Should be true    ${node_count} > ${4}

Future major version bump imports are rejected
    ${future_file}=    Modify export file with future major version number    ${prior_export}
    Run keyword and expect error    *incompatible RobotMBT version
    ...                             Import graph data from    ${future_file}

Future minor verion bump imports are accepted
    ${future_file}=    Modify export file with future minor version number    ${prior_export}
    Import graph data from    ${future_file}
    ${node_count}=    Number of graph nodes
    Should be equal    ${node_count}    ${4}

Ill-formed files are rejected for import
    ${corrupted_file}=    Corrupt export file    ${prior_export}
    Run keyword and expect error    *could not be loaded as RobotMBT graph data
    ...                             Import graph data from    ${corrupted_file}
