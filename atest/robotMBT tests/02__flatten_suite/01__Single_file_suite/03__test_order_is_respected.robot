*** Settings ***
Documentation     When flattening, setup and teardown are included in the scenario itself. Their order must be respected.
Suite Setup       Suite Setup
Suite Teardown    Should be equal    ${kw_count}    ${7}
Library           robotmbt    processor=flatten

*** Test Cases ***
first test case
    [Setup]    Test 1 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${2}

second test case
    [Setup]    Test 2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${4}
    [Teardown]    Test 2 teardown

third test case
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${6}
    [Teardown]    Test 3 teardown

*** Keywords ***
Suite setup
    Set Global Variable    ${kw_count}    ${0}
    Treat this test suite Model-based

Test 1 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${1}

Test 2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${3}

Test 2 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${5}

Test 3 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${7}
