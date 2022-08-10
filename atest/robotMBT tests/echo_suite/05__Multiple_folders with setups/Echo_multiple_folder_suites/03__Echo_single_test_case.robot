*** Settings ***
Suite Setup       Set Global Variable    ${setup_count}    ${setup_count+1}

*** Test Cases ***
first test case
    Set Global Variable    ${test_count}    ${test_count+1}
