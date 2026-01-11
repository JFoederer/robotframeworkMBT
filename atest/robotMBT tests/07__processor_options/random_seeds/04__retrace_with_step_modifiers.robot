*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace
...               and includes step modifiers. The suite passes if the recorded trace is reproduced
...               exactly as indicated by the trace string. Following the background all scenarios
...               are equally valid. Even though the content of each scenario is identical, data
...               included, the modifers will number the scenarios at random. The reproduced trace
...               must match for both the scenario order and the data order.
Suite Setup       Treat this test suite Model-based    seed=iulr-vih-esycu-eyl-yfa
Suite Teardown    Should be equal    ${trace}    H2G3C1E7I5B9F0A4D6J8
Library           robotmbt

*** Test Cases ***
Background
    Given suite is prepared

scenario A
    scenario A is executed
    when scenario number 0 is executed

scenario B
    scenario B is executed
    when scenario number 0 is executed

scenario C
    scenario C is executed
    when scenario number 0 is executed

scenario D
    scenario D is executed
    when scenario number 0 is executed

scenario E
    scenario E is executed
    when scenario number 0 is executed

scenario F
    scenario F is executed
    when scenario number 0 is executed

scenario G
    scenario G is executed
    when scenario number 0 is executed

scenario H
    scenario H is executed
    when scenario number 0 is executed

scenario I
    scenario I is executed
    when scenario number 0 is executed

scenario J
    scenario J is executed
    when scenario number 0 is executed

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

scenario number ${n} is executed
    [Documentation]    *model info*
    ...    :MOD: ${n}= trace.remaining
    ...    :IN:  None
    ...    :OUT: trace.remaining.remove(${n})
    Set Suite Variable    ${trace}    ${trace}${n}
