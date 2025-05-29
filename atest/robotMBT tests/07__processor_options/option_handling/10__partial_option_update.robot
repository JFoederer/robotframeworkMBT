*** Settings ***
Suite Setup       Run keywords    Set suite variable    ${test_count}    ${0}
...                        AND    Set model-based options    &{mbt_options}
...                        AND    Treat this test suite Model-based    bonus_scenario=${False}
Suite Teardown    Should be equal    ${test_count}    ${2}
Library           suiterepeater.py
Library           robotmbt    processor_lib=suiterepeater

*** Variables ***
&{mbt_options}    repeat=2    bonus_scenario=${True}

*** Test Cases ***
only test case
    Set suite variable    ${test_count}    ${test_count+1}
