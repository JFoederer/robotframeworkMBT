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
    ...    :OUT: new args
    No Operation

Keyword with ${emb_arg} as embedded argument
    [Documentation]    *model info*
    ...    :IN: args.emb_arg = ${emb_arg}
    ...    :OUT: args.emb_arg == Green
    RETURN    ${emb_arg}

Keyword with positional argument
    [Documentation]    *model info*
    ...    :IN: args.pos1 = ${pos1}
    ...    :OUT: args.pos1 == Green
    [Arguments]    ${pos1}
    RETURN    ${pos1}

Keyword with multiple positional arguments
    [Documentation]    *model info*
    ...    :IN: args.pos1 = ${pos1} | args.pos2 = ${pos2}
    ...    :OUT: args.pos1 == Green | args.pos2 == Red
    [Arguments]    ${pos1}    ${pos2}
    RETURN    ${pos1}    ${pos2}

Keyword with positional arguments and optional argument
    [Documentation]    *model info*
    ...    :IN: args.pos1 = ${pos1} | args.pos2 = ${pos2} | args.pos3 = ${pos3}
    ...    :OUT: args.pos1 == Green | args.pos2 == Red | args.pos3 == ${pos3}
    [Arguments]    ${pos1}    ${pos2}    ${pos3}=Orange
    RETURN    ${pos1}    ${pos2}    ${pos3}

Keyword with variable number of arguments
    [Documentation]    *model info*
    ...    :IN: args.varargs = ${varargs} | args.vararg1 = ${varargs}[0]
    ...    :OUT: len(args.varargs) == 3 | args.vararg1 == Green
    ...          args.varargs[0] == Green | args.varargs[1] == Red | args.varargs[2] == Blue
    [Arguments]    @{varargs}
    RETURN    ${varargs}

Keyword with named argument
    [Documentation]    *model info*
    ...    :IN: args.named1 = ${named1}
    ...    :OUT: args.named1 == Green
    [Arguments]    ${named1}=
    RETURN    ${named1}

Keyword with multiple named arguments
    [Documentation]    *model info*
    ...    :IN: args.named1 = ${named1} | args.named2 = ${named2}
    ...    :OUT: args.named1 == Green | args.named2 == Red
    [Arguments]    ${named1}=    ${named2}=
    RETURN    ${named1}    ${named2}

Keyword with free named arguments
    [Documentation]    *model info*
    ...    :IN: args.free = ${free} | args.free1 = ${free}[free1]
    ...    :OUT: len(args.free) == 3 | args.free1 == Green
    ...          args.free[free1] == Green | args.free[free2] == Red | args.free[free3] == Blue
    [Arguments]    &{free}
    RETURN    ${free}

Keyword with all ${emb_arg} argument styles mixed
    [Documentation]    *model info*
    ...    :IN: new combiargs | combiargs.emb_var = ${emb_arg}
    ...         combiargs.pos1 = ${pos1} | combiargs.pos2 = ${pos2}
    ...         combiargs.varargs = ${varargs} | combiargs.vararg1 = ${varargs}[0]
    ...         combiargs.named1 = ${named1} | combiargs.named2 = ${named2}
    ...         combiargs.free = ${free} | combiargs.free1 = ${free}[free1]
    ...    :OUT: combiargs.emb_var == 5
    ...          combiargs.pos1 == A | combiargs.pos2 == B
    ...          len(combiargs.varargs) == 2 | combiargs.vararg1 == C
    ...          combiargs.varargs[0] == C | combiargs.varargs[1] == D
    ...          combiargs.named1 == E | combiargs.named2 == F
    ...          len(combiargs.free) == 2 | combiargs.free1 == G
    ...          combiargs.free[free1] == G | combiargs.free[free2] == H
    ...          del combiargs
    [Arguments]    ${pos1}    ${pos2}    @{varargs}    ${named1}=    ${named2}=    &{free}
    VAR    &{all_args}=    emb_arg=${emb_arg}    pos1=${pos1}    pos2=${pos2}
    ...                    var_args=${varargs}    named1=${named1}    named2=${named2}    &{free}
    RETURN    ${all_args}

Keyword with ${emb_arg} argument styles mixed (no OUT-check)
    [Documentation]    *model info*
    ...    :IN: new combiargs | combiargs.emb_var = ${emb_arg}
    ...         combiargs.pos1 = ${pos1} | combiargs.pos2 = ${pos2}
    ...         combiargs.named1 = ${named1} | combiargs.named2 = ${named2}
    ...         combiargs.varargs = ${varargs} | combiargs.free = ${free}
    ...    :OUT: del combiargs
    [Arguments]    ${pos1}    ${pos2}    @{varargs}    ${named1}=    ${named2}=the default    &{free}
    VAR    &{all_args}=    emb_arg=${emb_arg}    pos1=${pos1}    pos2=${pos2}
    ...                    var_args=${varargs}    named1=${named1}    named2=${named2}    &{free}
    RETURN    ${all_args}
