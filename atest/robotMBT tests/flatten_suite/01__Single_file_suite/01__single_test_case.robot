*** Settings ***
Suite Setup       Suite Setup
Suite Teardown    Should be equal    ${kw_count}    ${1}
Library           robotmbt    processor=flatten

*** Test Cases ***
first test case
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${1}
    
*** Keywords ***
Suite setup
    Set Global Variable    ${kw_count}    ${0}
    Treat this test suite Model-based

