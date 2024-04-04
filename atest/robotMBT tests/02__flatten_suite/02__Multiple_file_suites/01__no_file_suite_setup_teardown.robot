*** Settings ***
Documentation     When flattening, setup and teardown are included in the scenario itself. Their order must be respected.
Library           robotmbt    processor=flatten

*** Test Cases ***
test case 1.1
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${1}
    [Teardown]    Test 1.1 teardown

test case 1.2
    [Setup]    Test 1.2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${4}
    [Teardown]    Test 1.2 teardown

test case 1.3
    [Setup]    Test 1.3 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${7}


