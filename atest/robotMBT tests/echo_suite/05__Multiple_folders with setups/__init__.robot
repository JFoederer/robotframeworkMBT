*** Settings ***
Suite Setup       Setup check variables

*** Keywords ***
Setup check variables
    Set Global Variable    ${test_count}    ${0}
    Set Global Variable    ${setup_count}    ${0}
