*** Settings ***
Suite Setup       Run keywords    Set Global Variable    ${test_count}    ${0}
...                        AND    Set model-based options    repeat=2    bonus_scenario=${True}
...                        AND    Set model-based options
...                        AND    Treat this test suite Model-based
Suite Teardown    Should be equal    ${test_count}    ${1}
Library           SuiteRepeater.py
Library           robotmbt    processor_lib=SuiteRepeater

*** Test Cases ***
only test case
    Set Global Variable    ${test_count}    ${test_count+1}
