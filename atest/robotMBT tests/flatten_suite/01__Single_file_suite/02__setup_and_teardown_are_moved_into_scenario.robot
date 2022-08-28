*** Settings ***
Documentation     When flattening, setup and teardown are included in the scenario itself. Their order must be respected.
Suite Setup       Suite Setup
Suite Teardown    Should be equal    ${kw_count}    ${3}
Library           robotmbt    processor=flatten

*** Test Cases ***
first test case
    [Setup]    Test setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${2}
    [Teardown]    Test teardown

*** Keywords ***
Suite setup
    Set Global Variable    ${kw_count}    ${0}
    Treat this test suite Model-based

Test setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${1}

Test teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${3}
