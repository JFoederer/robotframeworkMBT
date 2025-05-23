*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace
...               and includes step modifiers. The suite passes if the recorded trace is reproduced
...               exactly as indicated by the trace string. Following the background all scenarios
...               are equally valid. Even though the content of each scenario is identical, data
...               included, the modifers will number the test at random. The reproduced trace must
...               match for both the scenario order and the data order.
Suite Setup       Treat this test suite Model-based    seed=iulr-vih-esycu-eyl-yfa
Suite Teardown    Should be equal    ${trace}    H6G3E5I4D9F8J2B1A7C0
Library           robotmbt

*** Test Cases ***
Background
    Given suite is prepared

test case A
    scenario A is executed
    when test number 0 is executed

test case B
    scenario B is executed
    when test number 0 is executed

test case C
    scenario C is executed
    when test number 0 is executed

test case D
    scenario D is executed
    when test number 0 is executed

test case E
    scenario E is executed
    when test number 0 is executed

test case F
    scenario F is executed
    when test number 0 is executed

test case G
    scenario G is executed
    when test number 0 is executed

test case H
    scenario H is executed
    when test number 0 is executed

test case I
    scenario I is executed
    when test number 0 is executed

test case J
    scenario J is executed
    when test number 0 is executed

*** Keywords ***
suite is prepared
    [Documentation]    *model info*
    ...    :IN:  new trace | trace.remaining = list(range(10))
    ...    :OUT: None
    Set suite variable    ${trace}    ${empty}

scenario ${X} is executed
    [Documentation]    *model info*
    ...    :IN:  None
    ...    :OUT: None
    Set Suite Variable    ${trace}    ${trace}${X}

test number ${n} is executed
    [Documentation]    *model info*
    ...    :MOD: ${n}= trace.remaining
    ...    :IN:  None
    ...    :OUT: trace.remaining.remove(${n})
    Set Suite Variable    ${trace}    ${trace}${n}
