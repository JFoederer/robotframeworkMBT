*** Settings ***
Suite Setup       Suite setup
Suite Teardown    Should be equal    ${kw_count}    ${6}
Library           robotmbt    processor=flatten

    
*** Keywords ***
Suite setup
    Set Global Variable    ${kw_count}    ${0}
    Treat this test suite Model-based
