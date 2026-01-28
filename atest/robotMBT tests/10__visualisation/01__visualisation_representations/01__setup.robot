*** Settings ***   
Library           robotmbt    processor=flatten

*** Test Cases ***
Feature Setup
    Given test suite s has trace info t
    Then the algorithm inserts 'A1' with state "attr: states = ['a1'], special='!'"
    And the algorithm inserts 'A2' with state "attr: states = ['a1', 'a2'], special='!'"