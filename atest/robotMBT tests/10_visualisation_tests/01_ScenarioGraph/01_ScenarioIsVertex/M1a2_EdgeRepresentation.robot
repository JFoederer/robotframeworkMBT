*** Settings ***
Resource          ../../../../resources/visualisation.resource
Library           robotmbt    processor=echo

*** Test Cases ***
Graph should contain edge from vertex A to vertex B if B can be reached from A
    Given Test Suite s exists
    Given Test Suite s contains scenario Drive To Destination
    Given Test Suite s contains scenario Arrive At Destination
    Given In Test Suite s, scenario Arrive At Destination can be reached from Drive To Destination
    When Graph g is generated based on Test Suite s
    Then Graph g shows an edge from Drive To Destination towards Arrive At Destination
