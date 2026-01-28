*** Settings ***   
Library           robotmbt    processor=flatten

*** Test Cases ***
Vertex Scenario graph
    Given trace info t
    When scenario graph g is generated
    Then graph g contains vertex 'start'
    And graph g contains vertex 'A1'
    And graph g contains vertex 'A2'

Edge Scenario graph
    Given trace info t
    When scenario graph g is generated
    Then graph g has an edge from 'start' to 'A1'
    And graph g has an edge from 'A1' to 'A2'
    And graph g does not have an edge from 'start' to 'A2'
    And graph g does not have an edge from 'A2' to 'A1'
    And graph g does not have an edge from 'A2' to 'start'

Visual location of vertices scenario
    Given trace info t
    When scenario graph g is generated
    Then graph g has vertices 'start', 'A1', 'A2'
    And vertex 'start' is placed above 'A1'
    And vertex 'A1' is placed above 'A2'
