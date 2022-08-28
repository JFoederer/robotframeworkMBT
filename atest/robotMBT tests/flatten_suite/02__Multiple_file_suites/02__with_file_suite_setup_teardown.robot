*** Settings ***
Documentation     When flattening, setup and teardown are included in the scenario itself. Their order must be respected.
Suite Setup       Set Global Variable    ${kw_count}    ${kw_count+1}
Suite Teardown    Set Global Variable    ${kw_count}    ${kw_count+1}
Library           robotmbt    processor=flatten

*** Test Cases ***
test case 2.1
    [Setup]    Test 2.1 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${10}

test case 2.2
    [Setup]    Test 2.2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${14}
    [Teardown]    Test 2.2 teardown

test case 2.3
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${18}
    [Teardown]    Test 2.3 teardown
