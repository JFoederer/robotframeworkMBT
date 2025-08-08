*** Settings ***
Documentation     This test suites focuses on variations in which keywords receive arguments and
...               how they are made available for use in the models.
...               Note that in this suite the value checks are included (hard coded) in the :OUT:
...               expressions of the keyword. This is because we need to check that all data lands
...               correctly in the model.
Suite Setup       Treat this test suite Model-based
Library           robotmbt

*** Test Cases ***
No arguments
    Keyword without arguments

Embedded argument
    Keyword with Green as embedded argument

Positional arguments
    Keyword with positional argument    Green
    Keyword with multiple positional arguments    Green    pos2=Red

Variable number of arguments
    Keyword with variable number of arguments    Green    Red    Blue

Named arguments
    Keyword with named argument    named1=Green
    Keyword with multiple named arguments    named1=Green    named2=Red

Free named arguments
    Keyword with free named arguments    free1=Green    free2=Red    free3=Blue

Mixed argument styles
    Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H

BDD style with arguments
    Given Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H
    Then Keyword with all 5 argument styles mixed    A    B    C    D    named1=E    named2=F    free1=G    free2=H

*** Keywords ***
Keyword without arguments
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new args
    No Operation

Keyword with ${emb_var} as embedded argument
    [Documentation]    *model info*
    ...    :IN: args.emb_var = ${emb_var}
    ...    :OUT: args.emb_var == Green
    No Operation

Keyword with positional argument
    [Documentation]    *model info*
    ...    :IN: args.pos1 = ${pos1}
    ...    :OUT: args.pos1 == Green
    [Arguments]    ${pos1}
    No Operation

Keyword with multiple positional arguments
    [Documentation]    *model info*
    ...    :IN: args.pos1 = ${pos1} | args.pos2 = ${pos2}
    ...    :OUT: args.pos1 == Green | args.pos2 == Red
    [Arguments]    ${pos1}    ${pos2}
    No Operation

Keyword with variable number of arguments
    [Documentation]    *model info*
    ...    :IN: args.varargs = ${varargs} | args.vararg1 = ${varargs}[0]
    ...    :OUT: len(args.varargs) == 3 | args.vararg1 == Green
    ...          args.varargs[0] == Green | args.varargs[1] == Red | args.varargs[2] == Blue
    [Arguments]    @{varargs}
    No Operation

Keyword with named argument
    [Documentation]    *model info*
    ...    :IN: args.named1 = ${named1}
    ...    :OUT: args.named1 == Green
    [Arguments]    ${named1}=
    No Operation

Keyword with multiple named arguments
    [Documentation]    *model info*
    ...    :IN: args.named1 = ${named1} | args.named2 = ${named2}
    ...    :OUT: args.named1 == Green | args.named2 == Red
    [Arguments]    ${named1}=    ${named2}=
    No Operation

Keyword with free named arguments
    [Documentation]    *model info*
    ...    :IN: args.free = ${free} | args.free1 = ${free}[free1]
    ...    :OUT: len(args.free) == 3 | args.free1 == Green
    ...          args.free[free1] == Green | args.free[free2] == Red | args.free[free3] == Blue
    [Arguments]    &{free}
    No Operation

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
    No Operation
