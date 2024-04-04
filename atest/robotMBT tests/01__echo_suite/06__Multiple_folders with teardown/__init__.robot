*** Settings ***
Suite Setup       Init teardown check variables

*** Keywords ***
Init teardown check variables
    Set Global Variable    ${test_count}    ${0}
    Set Global Variable    ${teardown_count}    ${0}
