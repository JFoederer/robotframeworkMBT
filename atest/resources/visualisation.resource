*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           robotmbt.visualise.visualiser.Visualiser  scenario
Library           Collections


*** Keywords ***
Test Suite ${suite} exists
    [Documentation]    Makes a test suite
    ...    :IN: suite = ${suite}
    ...    :OUT: None
    Set Suite Variable    ${suite}
    ${trace_info} =    Generate Trace Information   ${0}
    Set Suite Variable    ${trace_info}    # make empty trace info

Test Suite ${suite} has ${count} scenarios
    [Documentation]    Makes a test suite
    ...    :IN: scenario_count = ${count}, suite = ${suite}
    ...    :OUT: None
    ${trace_info} =    Generate Trace Information   ${count}
    Set Suite Variable    ${trace_info}

# WARNING: this only works for Scenario graphs, this needs to be adjusted to continually update the model when adding new state.
Test Suite ${suite} contains scenario ${scenario_name}
    [Documentation]    Ensures test suite Suite has scenario with name=Scenario name
    ...    :IN: suite = ${suite}, scenario_name = ${scenario_name}
    ...    :OUT: None
    Variable Should Exist    ${trace_info}

    ${trace_info} =    Ensure Scenario Present    ${trace_info}    ${scenario_name}
    Set Suite Variable    ${trace_info}

In Test Suite ${suite}, scenario ${s2} can be reached from ${s1}
    [Documentation]    Ensures a scenario s2 immediately follows s1 in a trace
    ...    :IN: suite = ${suite}, scenario2 = ${s2}, scenario1 = ${s1}
    ...    :OUT: None
    
    ${trace_info} =    Ensure Scenario Follows    ${trace_info}    ${s1}    ${s2}
    Set Suite Variable    ${trace_info}

Graph ${graph} of type ${graph_type} is generated based on Test Suite ${suite}
    [Documentation]    Generates the graph 
    ...    :IN: graph = ${graph}, graph_type = ${graph_type}, suite = ${suite}
    ...    :OUT: None
    Variable Should Exist    ${trace_info}
    ${visualiser} =    robotmbt.visualise.visualiser.Visualiser.Construct  graph_type=${graph_type}
    Call Method    ${visualiser}    update_visualisation    ${trace_info}
    ${html} =     Call Method    ${visualiser}    generate_visualisation

    Set Suite Variable    ${visualiser}
    Set Suite Variable    ${html}

Graph ${graph} contains ${number} vertices
    [Documentation]    Verifies that the graph contains the specified number of vertices.
    ...    :IN: graph = ${graph}, number = ${number}
    ...    :OUT: None
    Variable Should Exist    ${visualiser}
    Variable Should Exist    ${trace_info}
    
    ${vertex_count} =    Get Length   ${visualiser.graph.networkx.nodes}
    Should Be Equal As Integers       ${vertex_count}    ${number}

Graph ${graph} shows an edge from ${scenname1} towards ${scenname2}
    [Documentation]    Verifies that a generated graph contains a certain edge
    ...    :IN: graph = ${graph}, scenario name 1 = ${scenname1}, scenario name 2 = ${scenname2}
    ...    :OUT: None
    Variable Should Exist    ${visualiser}

    ${res} =     Ensure Edge Exists    ${visualiser.graph}    ${scenname1}    ${scenname2}