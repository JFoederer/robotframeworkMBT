*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace.
...               The suite consists of 10 independent test cases, giving 10! (>3.500.000) possible
...               traces. The suite passes if the recorded trace is reproduced exactly, as
...               indicated by the number string.
Suite Setup       Run keywords    Set suite variable    ${trace}    ${empty}
...                        AND    Treat this test suite Model-based    seed=aqmou-eelcuu-sniu-ugsyek-jyhoor
Suite Teardown    Should be equal    ${trace}    6930142758
Library           robotmbt

*** Test Cases ***
test case 0
    test number 0 is executed

test case 1
    test number 1 is executed

test case 2
    test number 2 is executed

test case 3
    test number 3 is executed

test case 4
    test number 4 is executed

test case 5
    test number 5 is executed

test case 6
    test number 6 is executed

test case 7
    test number 7 is executed

test case 8
    test number 8 is executed

test case 9
    test number 9 is executed

*** Keywords ***
test number ${n} is executed
    [Documentation]    *model info*
    ...    :IN:  None
    ...    :OUT: None
    Set Suite Variable    ${trace}    ${trace}${n}
