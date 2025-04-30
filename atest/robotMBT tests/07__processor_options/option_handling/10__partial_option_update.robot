*** Settings ***
Suite Setup       Run keywords    Set Global Variable    ${test_count}    ${0}
...                        AND    Set model-based options    &{mbt_options}
...                        AND    Treat this test suite Model-based    bonus_scenario=${False}
Suite Teardown    Should be equal    ${test_count}    ${2}
Library           SuiteRepeater.py
Library           robotmbt    processor_lib=SuiteRepeater

*** Variables ***
&{mbt_options}    repeat=2    bonus_scenario=${True}

*** Test Cases ***
only test case
    Set Global Variable    ${test_count}    ${test_count+1}
