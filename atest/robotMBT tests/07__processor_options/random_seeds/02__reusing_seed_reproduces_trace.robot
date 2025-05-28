*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace.
...               The suite consists of 10 independent scenarios, giving 10! (>3.500.000) possible
...               traces. The suite passes if the recorded trace is reproduced exactly, as
...               indicated by the number string.
Suite Setup       Run keywords    Set suite variable    ${trace}    ${empty}
...                        AND    Treat this test suite Model-based    seed=aqmou-eelcuu-sniu-ugsyek-jyhoor
Suite Teardown    Should be equal    ${trace}    6930142758
Library           robotmbt

*** Test Cases ***
scenario 0
    scenario number 0 is executed

scenario 1
    scenario number 1 is executed

scenario 2
    scenario number 2 is executed

scenario 3
    scenario number 3 is executed

scenario 4
    scenario number 4 is executed

scenario 5
    scenario number 5 is executed

scenario 6
    scenario number 6 is executed

scenario 7
    scenario number 7 is executed

scenario 8
    scenario number 8 is executed

scenario 9
    scenario number 9 is executed

*** Keywords ***
scenario number ${n} is executed
    [Documentation]    *model info*
    ...    :IN:  None
    ...    :OUT: None
    Set Suite Variable    ${trace}    ${trace}${n}
