*** Settings ***
Suite Setup       Run keywords    Set Global Variable    ${test_count}    ${0}
...                        AND    Treat this test suite Model-based    repeat=2
Suite Teardown    Should be equal    ${test_count}    ${2}
Library           SuiteRepeater.py
Library           robotmbt    processor_lib=SuiteRepeater

*** Test Cases ***
only test case
    Set Global Variable    ${test_count}    ${test_count+1}
