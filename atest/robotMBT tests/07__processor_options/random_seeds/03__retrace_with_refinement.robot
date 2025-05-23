*** Settings ***
Documentation     This suite uses the `seed` argument to reproduce a previously generated trace
...               and includes step refinement. The suite passes if the recorded trace is
...               reproduced exactly as indicated by the trace string. Refinement goes two levels
...               deep with high-, mid- and low-level scenarios. Scenarios on the same level are
...               interchangeable. The special catch is that the high-level scenarios can be
...               directly refined by a low-level scenario, or in two layers where the mid-level
...               scenario is refined by the low-level scenario. This catch makes different valid
...               traces possible of varying length.
Suite Setup       Run keywords    Set suite variable    ${trace}    ${empty}
...                        AND    Treat this test suite Model-based    seed=xou-pumj-ihj-oibiyc-surer
Suite Teardown    Should be equal    ${trace}    B1A5BY3B4BX6B2
Library           robotmbt

*** Test Cases ***
high-level A
    test A is executed
    when refining high-level scenario

high-level B
    test B is executed
    when refining high-level scenario

mid-level X
    test X is executed
    when refining mid-level scenario

mid-level Y
    test Y is executed
    when refining mid-level scenario

low-level 1
    test 1 is executed
    when refinement is done by low-level scenario

low-level 2
    test 2 is executed
    when refinement is done by low-level scenario

low-level 3
    test 3 is executed
    when refinement is done by low-level scenario

low-level 4
    test 4 is executed
    when refinement is done by low-level scenario

low-level 5
    test 5 is executed
    when refinement is done by low-level scenario

low-level 6
    test 6 is executed
    when refinement is done by low-level scenario

*** Keywords ***
refining high-level scenario
    [Documentation]    *model info*
    ...    :IN:  scenario.level = high
    ...    :OUT: scenario.level == low
    Log    Action delegated to lower level

refining mid-level scenario
    [Documentation]    *model info*
    ...    :IN:  scenario.level == high | scenario.level = mid
    ...    :OUT: scenario.level == low
    VAR    ${exe_check}    ${True}

refinement is done by low-level scenario
    [Documentation]    *model info*
    ...    :IN:  scenario.level
    ...    :OUT: scenario.level = low
    VAR    ${exe_check}    ${True}

test ${n} is executed
    [Documentation]    *model info*
    ...    :IN:  None
    ...    :OUT: None
    Set Suite Variable    ${trace}    ${trace}${n}
