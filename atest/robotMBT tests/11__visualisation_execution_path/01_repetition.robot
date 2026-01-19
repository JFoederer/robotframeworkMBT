*** Settings ***
Documentation     
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/visualisation.resource
Library           robotmbt

*** Test Cases ***
Setup
    Given test suite s has trace info t
    Then the algorithm inserts 'A1' with state "attr: states=['a1'],special='!'"
    And the algorithm inserts 'A1' with state "attr: states=['a1'],special='!'"    
    And the algorithm inserts 'B1' with state "attr: states=['a1','b1'], special='!'"
    And the algorithm inserts 'B2' with state "attr: states=['a1','b1','b2'], special='!'"
    And the algorithm inserts 'B1' with state "attr: states=['a1','b1','b2'], special='!'"

Self-loop
    Given trace info t
    When scenario graph g is generated
    Then graph g contains vertex 'A1'
    And graph g has an edge from 'A1' to 'A1'

Two-vertex loop
    Given trace info t
    When scenario graph g is generated
    Then graph g contains vertex 'B1'
    And graph g contains vertex 'B2'
    And graph g has an edge from 'B1' to 'B2'
    And graph g has an edge from 'B2' to 'B1'