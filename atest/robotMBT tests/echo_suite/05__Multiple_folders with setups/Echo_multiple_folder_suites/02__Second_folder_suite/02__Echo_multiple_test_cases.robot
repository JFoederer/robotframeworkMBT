*** Test Cases ***
first test case
    [Setup]    Set Global Variable    ${setup_count}    ${setup_count+1}
    Set Global Variable    ${test_count}    ${test_count+1}

second test case
    Set Global Variable    ${test_count}    ${test_count+1}

third test case
    [Setup]    Set Global Variable    ${setup_count}    ${setup_count+1}
    Set Global Variable    ${test_count}    ${test_count+1}
