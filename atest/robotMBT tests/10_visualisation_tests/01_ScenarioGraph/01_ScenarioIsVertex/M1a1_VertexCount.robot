*** Settings ***
Resource          ../../../../resources/visualisation.resource
Library           robotmbt    processor=echo
Suite Setup       Set Global Variable    ${scen_count}    ${2}

*** Test Cases ***
Graph should contain vertex count equal to scenario count + 1 for scenario-graph
    Given Test Suite s exists
    Given Test Suite s has ${scen_count} scenarios
    When Graph g is generated based on Test Suite s
    Then Graph g contains ${scen_count + 1} vertices