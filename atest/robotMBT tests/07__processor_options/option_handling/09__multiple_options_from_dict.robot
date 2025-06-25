*** Settings ***
Suite Setup       Run keywords    Set suite variable    ${test_count}    ${0}
...                        AND    Treat this test suite Model-based    &{mbt_options}
Suite Teardown    Should be equal    ${test_count}    ${3}
Library           suiterepeater.py
Library           robotmbt    processor_lib=suiterepeater

*** Variables ***
&{mbt_options}    repeat=2    bonus_scenario=${True}

*** Test Cases ***
only test case
    Set suite variable    ${test_count}    ${test_count+1}
