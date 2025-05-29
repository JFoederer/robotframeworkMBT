*** Settings ***
Suite Setup       Run keywords    Set suite variable    ${test_count}    ${0}
...                        AND    Set model-based options    repeat=2
...                        AND    Treat this test suite Model-based    repeat=3
Suite Teardown    Should be equal    ${test_count}    ${3}
Library           suiterepeater.py
Library           robotmbt    processor_lib=suiterepeater

*** Test Cases ***
only test case
    Set suite variable    ${test_count}    ${test_count+1}
