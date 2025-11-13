*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           robotmbt.visualise.visualiser.Visualiser
Library           Collections


*** Keywords ***
Test Suite ${suite} exists
    [Documentation]    Makes a test suite
    ...    :IN: suite = ${suite}
    ...    :OUT: None
    Set Suite Variable    ${suite}

Test Suite ${suite} has ${count} scenarios
    [Documentation]    Makes a test suite
    ...    :IN: scenario_count = ${count}, suite = ${suite}
    ...    :OUT: None
    # use customer ScenarioGenerator.py to generate some scenarios
    
    ${trace_info} =    Generate Trace Information   ${count}
    Set Suite Variable    ${trace_info}

# WARNING: this only works for Scenario graphs, this needs to be adjusted to continually update the model when adding new state.
Graph ${graph} is generated based on Test Suite ${suite}
     [Documentation]    Generates the graph 
    ...    :IN: graph = ${graph}, suite = ${suite}
    ...    :OUT: None
    Variable Should Exist    ${trace_info}
    ${visualiser} =    robotmbt.visualise.visualiser.Visualiser.Construct
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


