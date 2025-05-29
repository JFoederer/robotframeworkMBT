*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace
...               and includes a combination of sequencing, refinement and step modifiers. The
...               suite passes if the recorded trace is reproduced exactly as indicated by the
...               trace string. There are a number of things to take into account with this test
...               suite.
...               The run must always start with the leading scenario, inserting A, followed by a
...               center loop, inserting P, Q, R, S or T at random a number of times, followed by
...               a tail of scenarios X and Y in order.
...               X is constructed in such a way that it can follow the center loop whenever
...               scenario P was chosen. Since X is readily available after each P, it is expected
...               to be inserted while the loop still needs to continue further. This forces a
...               rollback into the process of the algorithm.
...               The looping part is enhanced with refinement. The high-level scenario includes
...               a data choice by using step modifiers. The lower level includes a path choice.
...               Both low-level scenarios are equally valid, the only difference is that the data
...               choice is included either once or twice.
Suite Setup       Treat this test suite Model-based    seed=gujuqt-iakm-oexo-xnu-huba
Suite Teardown    Should be equal    ${trace}    ATQQPRSPRPXY
Library           robotmbt

*** Test Cases ***
leading scenario
    given suite is prepared
    when executing scenario A
    then scenario A is executed

high-level center loop
    given scenario A is executed
    when scenario is refined into P with choice
    then scenario P is executed from choice

low-level center loop single
    given scenario X is not yet executed
    when executing scenario P with choice
    then scenario P is executed from choice

low-level center loop double
    given scenario X is not yet executed
    when executing scenario P with choice
    and executing scenario P with choice
    then scenario P is executed from choice

first trailing scenario
    given scenario P is the latest scenario
    when executing scenario X
    then scenario X is executed

second trailing scenario
    given scenario X is the latest scenario
    and trace length is longer than 9
    when executing scenario Y
    then scenario Y is executed

*** Keywords ***
suite is prepared
    [Documentation]    *model info*
    ...    :IN:  new trace | trace.scenarios = []
    ...    :OUT: None
    Set suite variable    ${trace}    ${empty}

executing scenario ${x}
    [Documentation]    *model info*
    ...    :IN:  trace.scenarios
    ...    :OUT: trace.scenarios.append(${x})
    Set Suite Variable    ${trace}    ${trace}${x}

scenario ${x} is executed
    [Documentation]    *model info*
    ...    :IN:  ${x} in trace.scenarios
    ...    :OUT: ${x} in trace.scenarios
    Should contain    ${trace}    ${x}

executing scenario ${x} with choice
    [Documentation]    *model info*
    ...    :MOD: ${x} = [scenario.choice]
    ...    :IN:  trace.scenarios
    ...    :OUT: trace.scenarios.append(${x})
    Set Suite Variable    ${trace}    ${trace}${x}

scenario ${x} is executed from choice
    [Documentation]    *model info*
    ...    :MOD: ${x} = ['P', 'Q', 'R', 'S', 'T']
    ...    :IN:  trace.scenarios[-1] == ${x}
    ...    :OUT: trace.scenarios[-1] == ${x}
    Should Be Equal    ${trace}[-1]    ${x}

scenario is refined into ${x} with choice
    [Documentation]    *model info*
    ...    :MOD: ${x} = [x for x  in ('P', 'Q', 'R', 'S', 'T') if x != trace.scenarios[-1]]
    ...    :IN:  trace.scenarios[-1] != ${x} | scenario.choice = ${x}
    ...    :OUT: trace.scenarios[-1] == ${x}
    Should Be Equal    ${trace}[-1]    ${x}

scenario ${x} is the latest scenario
    [Documentation]    *model info*
    ...    :IN:  trace.scenarios[-1] == ${x}
    ...    :OUT: trace.scenarios[-1] == ${x}
    Should Be Equal    ${trace}[-1]    ${x}

scenario ${x} is not yet executed
    [Documentation]    *model info*
    ...    :IN:  ${x} not in trace.scenarios
    ...    :OUT: ${x} not in trace.scenarios
    Should not contain    ${trace}    ${x}

trace length is longer than ${n}
    [Documentation]    *model info*
    ...    :IN:  len(trace.scenarios) > ${n}
    ...    :OUT: len(trace.scenarios) > ${n}
    ${len}=    Get Length    ${trace}
    IF    ${len}<=${n}
        Fail    Too short
    END
