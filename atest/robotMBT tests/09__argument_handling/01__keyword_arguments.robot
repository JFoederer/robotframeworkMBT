*** Settings ***
Documentation     This test suite focuses on variations in which keywords receive arguments and how
...               they are made available for use in the models.
...               Note that in this suite the value checks are included (hard coded) in the :OUT:
...               expressions of the keyword. This is because we need to check that all data lands
...               correctly in the model.
Suite Setup       Treat this test suite Model-based
Library           robotmbt

*** Test Cases ***
No arguments
    Keyword without arguments

Embedded argument
    ${emb_arg}=    Keyword with Green as embedded argument
    Should be equal    ${emb_arg}    Green

Positional arguments
    ${pos1}=    Keyword with positional argument    Green
    Should be equal    ${pos1}    Green
    ${pos1}    ${pos2}=    Keyword with multiple positional arguments    Green    Red
    Should be equal    ${pos1}    Green
    Should be equal    ${pos2}    Red

Optional argument
    ${pos1_a}    ${pos2_a}    ${pos3_a}=    Keyword with positional arguments and optional argument    Green    Red
    Should be equal    ${pos1_a}    Green
    Should be equal    ${pos2_a}    Red
    Should be equal    ${pos3_a}    Orange
    ${pos1_b}    ${pos2_b}    ${pos3_b}=    Keyword with positional arguments and optional argument    Green    Red    Blue
    Should be equal    ${pos1_b}    Green
    Should be equal    ${pos2_b}    Red
    Should be equal    ${pos3_b}    Blue

Variable number of arguments
    @{varargs}=    Keyword with variable number of arguments    Green    Red    Blue
    Should be equal    ${varargs}[0]    Green
    Should be equal    ${varargs}[1]    Red
    Should be equal    ${varargs}[2]    Blue

Named arguments
    ${named1_a}=    Keyword with named argument    named1=Green
    Should be equal    ${named1_a}    Green
    ${named1_b}    ${named2}=    Keyword with multiple named arguments    named1=Green    named2=Red
    Should be equal    ${named1_b}    Green
    Should be equal    ${named2}    Red

Free named arguments
    &{free}=    Keyword with free named arguments    free1=Green    free2=Red    free3=Blue
    Should be equal    ${free}[free1]    Green
    Should be equal    ${free}[free2]    Red
    Should be equal    ${free}[free3]    Blue

Mixed argument styles
    &{all_args}=    Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H
    Should be equal    ${all_args}[emb_arg]    5
    Should be equal    ${all_args}[pos1]    A
    Should be equal    ${all_args}[pos2]    B
    Should be equal    ${all_args}[var_args][0]    C
    Should be equal    ${all_args}[var_args][1]    D
    Should be equal    ${all_args}[named1]    E
    Should be equal    ${all_args}[named2]    F
    Should be equal    ${all_args}[free1]    G
    Should be equal    ${all_args}[free2]    H

BDD style with arguments
    Given Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H
    Then Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H

Empty varargs and free named args
    &{all_args}=    Keyword with some argument styles mixed (no OUT-check)    A    B    named1=C
    ${n_varargs}=    Get length    ${all_args}[var_args]
    Should be equal    ${n_varargs}    ${0}
    Should be equal    ${all_args}[named2]    the default
    ${total_args}=    Get length    ${all_args}
    Should be equal    ${total_args}    ${6}

Shuffled argument ordering
    &{all_args}=    Keyword with some argument styles mixed (no OUT-check)    A    B    named2=C    free1=D    named1=E
    ${n_varargs}=    Get length    ${all_args}[var_args]
    Should be equal    ${n_varargs}    ${0}
    Should be equal    ${all_args}[named2]    C
    Should be equal    ${all_args}[free1]    D
    ${total_args}=    Get length    ${all_args}
    Should be equal    ${total_args}    ${7}


*** Keywords ***
Keyword without arguments
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    No Operation

Keyword with ${emb_arg} as embedded argument
    [Documentation]    *model info*
    ...    :IN: scenario.emb_arg = ${emb_arg}
    ...    :OUT: scenario.emb_arg == Green
    RETURN    ${emb_arg}

Keyword with positional argument
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1}
    ...    :OUT: scenario.pos1 == Green
    [Arguments]    ${pos1}
    RETURN    ${pos1}

Keyword with multiple positional arguments
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2}
    ...    :OUT: scenario.pos1 == Green | scenario.pos2 == Red
    [Arguments]    ${pos1}    ${pos2}
    RETURN    ${pos1}    ${pos2}

Keyword with positional arguments and optional argument
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2} | scenario.pos3 = ${pos3}
    ...    :OUT: scenario.pos1 == Green | scenario.pos2 == Red | scenario.pos3 == ${pos3}
    [Arguments]    ${pos1}    ${pos2}    ${pos3}=Orange
    RETURN    ${pos1}    ${pos2}    ${pos3}

Keyword with variable number of arguments
    [Documentation]    *model info*
    ...    :IN: scenario.varargs = ${varargs} | scenario.vararg1 = ${varargs}[0]
    ...    :OUT: len(scenario.varargs) == 3 | scenario.vararg1 == Green
    ...          scenario.varargs[0] == Green | scenario.varargs[1] == Red | scenario.varargs[2] == Blue
    [Arguments]    @{varargs}
    RETURN    ${varargs}

Keyword with named argument
    [Documentation]    *model info*
    ...    :IN: scenario.named1 = ${named1}
    ...    :OUT: scenario.named1 == Green
    [Arguments]    ${named1}=
    RETURN    ${named1}

Keyword with multiple named arguments
    [Documentation]    *model info*
    ...    :IN: scenario.named1 = ${named1} | scenario.named2 = ${named2}
    ...    :OUT: scenario.named1 == Green | scenario.named2 == Red
    [Arguments]    ${named1}=    ${named2}=
    RETURN    ${named1}    ${named2}

Keyword with free named arguments
    [Documentation]    *model info*
    ...    :IN: scenario.free = ${free} | scenario.free1 = ${free}[free1]
    ...    :OUT: len(scenario.free) == 3 | scenario.free1 == Green
    ...          scenario.free[free1] == Green | scenario.free[free2] == Red | scenario.free[free3] == Blue
    [Arguments]    &{free}
    RETURN    ${free}

Keyword with all ${emb_arg} argument styles mixed
    [Documentation]    *model info*
    ...    :IN: scenario.emb_var = ${emb_arg}
    ...         scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2}
    ...         scenario.varargs = ${varargs} | scenario.vararg1 = ${varargs}[0]
    ...         scenario.named1 = ${named1} | scenario.named2 = ${named2}
    ...         scenario.free = ${free} | scenario.free1 = ${free}[free1]
    ...    :OUT: scenario.emb_var == 5
    ...          scenario.pos1 == A | scenario.pos2 == B
    ...          len(scenario.varargs) == 2 | scenario.vararg1 == C
    ...          scenario.varargs[0] == C | scenario.varargs[1] == D
    ...          scenario.named1 == E | scenario.named2 == F
    ...          len(scenario.free) == 2 | scenario.free1 == G
    ...          scenario.free[free1] == G | scenario.free[free2] == H
    [Arguments]    ${pos1}    ${pos2}    @{varargs}    ${named1}=    ${named2}=    &{free}
    VAR    &{all_args}=    emb_arg=${emb_arg}    pos1=${pos1}    pos2=${pos2}
    ...                    var_args=${varargs}    named1=${named1}    named2=${named2}    &{free}
    RETURN    ${all_args}

Keyword with ${emb_arg} argument styles mixed (no OUT-check)
    [Documentation]    *model info*
    ...    :IN: scenario.emb_var = ${emb_arg}
    ...         scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2}
    ...         scenario.named1 = ${named1} | scenario.named2 = ${named2}
    ...         scenario.varargs = ${varargs} | scenario.free = ${free}
    ...    :OUT: None
    [Arguments]    ${pos1}    ${pos2}    @{varargs}    ${named1}=    ${named2}=the default    &{free}
    VAR    &{all_args}=    emb_arg=${emb_arg}    pos1=${pos1}    pos2=${pos2}
    ...                    var_args=${varargs}    named1=${named1}    named2=${named2}    &{free}
    RETURN    ${all_args}
