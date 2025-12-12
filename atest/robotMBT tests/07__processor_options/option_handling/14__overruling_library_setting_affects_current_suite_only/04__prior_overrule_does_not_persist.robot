*** Settings ***
Suite Setup       Run keywords    Set suite variable    ${test_count}    ${0}
...                        AND    Treat this test suite Model-based
Suite Teardown    Should be equal    ${test_count}    ${2}
Library           robotmbt    processor_lib=suiterepeater

*** Test Cases ***
only test case
    Set suite variable    ${test_count}    ${test_count+1}
