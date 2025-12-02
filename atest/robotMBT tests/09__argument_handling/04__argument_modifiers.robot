*** Settings ***
Documentation     This test suites focuses on using modifiers on non-embedded arguments.
...               A variation of colours is used as arguments. Modifers are set up in such a way
...               that, when modified:
...                 * Red turns to Green,
...                 * Yellow turns to Blue,
...                 * Orange is a default (unmodified) argument
...                 * Pink is never used in a test and alway comes from a modifier
...               Note that in this suite the value checks are also included (hard coded) in the
...               :OUT: expressions of the keyword. This is to check that all data lands correctly
...               in the model.
Suite Setup       Treat this test suite Model-based
Library           robotmbt

*** Test Cases ***
Positional arguments can be modified
    [Documentation]    Red is force modified to Green
    ${pos}=    Keyword with positional argument    Red
    Should be equal    ${pos}    Green

Multiple different positional arguments should stay different
    [Documentation]    The second argument is force modified to Blue, the first argument must be different
    ${one}    ${two}=    Keyword with multiple positional arguments    Red    Yellow
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue

Multiple same positional arguments should stay identical
    [Documentation]    The second argument is force modified to Blue, the first argument must follow
    ${one}    ${two}=    Keyword with multiple positional arguments    Yellow    Yellow
    Should be equal    ${one}    Blue
    Should be equal    ${two}    Blue

Unused optional arguments are not modified
    [Documentation]    ${opt} has the default value 'Orange' and ${opt} also has a modifier. The modifer does
    ...                does not have 'Orange' as a valid value. Because the argument is not used, its default
    ...                is used, regardless of the modifer.
    ${one}    ${two}    ${opt}=    Keyword with positional arguments and optional argument    Red    Yellow
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue
    Should be equal    ${opt}    Orange

Used optional arguments are modified
    [Documentation]    ${opt} has a default value and ${opt} also has a modifier. The modifier is triggered, because
    ...                 the argument is used and modifies 'Pink' into the only remaining option 'Purple'.
    ${one}    ${two}    ${opt}=    Keyword with positional arguments and optional argument    Red    Yellow    Purple
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue
    Should be equal    ${opt}    Pink

Used optional arguments are modified and matched with other example values
    [Documentation]    ${opt} has a default value and ${opt} also has a modifier. The modifier is triggered, because
    ...                 the argument is used and modifies 'Yellow' into Blue to match the second argument.
    ${one}    ${two}    ${opt}=    Keyword with positional arguments and optional argument    Red    Yellow    Yellow
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue
    Should be equal    ${opt}    Blue

Unused optional arguments are not modified regardless other matching example values
    [Documentation]    ${opt} has default value 'Orange', but this argument is not used. One of the other arguments
    ...                uses Orange as its example value, but after modification this is no longer a valid value. The
    ...                positional argument gets modified into one of its valid values, while the unused argument
    ...                keeps its default value.
    ${one}    ${two}    ${opt}=    Keyword with positional arguments and optional argument    Red    Orange
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue
    Should be equal    ${opt}    Orange

Used optional arguments are modified when set to the value that is the default
    [Documentation]    ${opt} has default value 'Orange', and this exact value happens to be used in the scenario.
    ...                'Orange' is however not a valid value after modification. Since the argument is used, the
    ...                modifier is triggered and set to a modified value.
    ${one}    ${two}    ${opt}=    Keyword with positional arguments and optional argument    Red    Yellow    Orange
    Should be equal    ${one}    Green
    Should be equal    ${two}    Blue
    Should be equal    ${opt}    Pink

Mixed argument types are matched on their example values
    &{all_args}=    Keyword with all Red argument styles mixed    Red    Yellow    named2=Red
    Should be equal    ${all_args}[emb]       Green
    Should be equal    ${all_args}[pos1]      Green
    Should be equal    ${all_args}[pos2]      Blue
    Should be equal    ${all_args}[named1]    Orange
    Should be equal    ${all_args}[named2]    Green

Varargs can be modified
    @{all_args}=    Keyword that expands its varargs    Red    Yellow
    VAR    @{expected}    Red    Yellow    Pink    Red
    Should Be Equal    ${all_args}    ${expected}

Varargs are not matched with other arguments
    &{all_args}=    Keyword with all Red argument styles mixed    Red    Yellow    Red    Blue    named2=Red
    Should be equal    ${all_args}[emb]           Green
    Should be equal    ${all_args}[pos1]          Green
    Should be equal    ${all_args}[pos2]          Blue
    Should be equal    ${all_args}[varargs][0]    Red       # Red from original argument, unaffected by other Red to Green modifiers
    Should be equal    ${all_args}[varargs][1]    Blue      # Blue from original argument, unaffected by other Yellow to Blue modifiers
    Should be equal    ${all_args}[varargs][2]    Pink      # Newly added argument by vararg modifier
    Should be equal    ${all_args}[varargs][3]    Red       # First vararg copied to the end unmodified
    Should be equal    ${all_args}[named1]        Orange
    Should be equal    ${all_args}[named2]        Green

Unused varargs skip their modifiers
    @{all_args}=    Keyword that expands its varargs
    Should Be Empty    ${all_args}

Free named arguments can be modified
    &{all_args}=    Keyword that expands free named arguments    colour1=Red    colour2=Yellow
    Should be equal    ${all_args}[colour1]      Red
    Should be equal    ${all_args}[colour2]      Blue
    Should be equal    ${all_args}[newcolour]    Pink
    Should be equal    ${all_args}[dupcolour]    Red

Unused free named arguments skip their modifiers
    &{all_args}=    Keyword that expands free named arguments
    Should Be Empty    ${all_args}

Free named arguments are not matched with other arguments
    &{all_args}=    Keyword with all Red argument styles mixed    Red    Yellow    Red    Blue
    ...             named2=Red    colour1=Red    colour2=Yellow
    Should be equal    ${all_args}[emb]           Green
    Should be equal    ${all_args}[pos1]          Green
    Should be equal    ${all_args}[pos2]          Blue
    Should be equal    ${all_args}[varargs][0]    Red
    Should be equal    ${all_args}[varargs][1]    Blue
    Should be equal    ${all_args}[varargs][2]    Pink
    Should be equal    ${all_args}[varargs][3]    Red
    Should be equal    ${all_args}[named1]        Orange
    Should be equal    ${all_args}[named2]        Green
    Should be equal    ${all_args}[colour1]       Red    # Red from original argument, unaffected by other Red to Green modifiers
    Should be equal    ${all_args}[colour2]       Blue   # Modified from Yellow to Blue by modifer
    Should be equal    ${all_args}[newcolour]     Pink   # Newly added named argument by modifier
    Should be equal    ${all_args}[dupcolour]     Red    # colour1 copied to dupcolour by modifier

*** Keywords ***
Keyword with positional argument
    [Documentation]    *model info*
    ...    :MOD: ${pos1}= [Green]
    ...    :IN: scenario.pos1 = ${pos1}
    ...    :OUT: scenario.pos1 == Green
    [Arguments]    ${pos1}
    RETURN    ${pos1}

Keyword with multiple positional arguments
    [Documentation]    *model info*
    ...    :MOD: ${pos1}= [Green, Blue] | ${pos2}= [Blue]
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2}
    ...    :OUT: scenario.pos1 == Green | scenario.pos2 == Blue
    [Arguments]    ${pos1}    ${pos2}
    RETURN    ${pos1}    ${pos2}

Keyword with positional arguments and optional argument
    [Documentation]    *model info*
    ...    :MOD: ${pos1}= [Green, Blue] | ${pos2}= [Blue] | ${pos3}=[Blue, Pink]
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2} | scenario.pos3 = ${pos3}
    ...    :OUT: scenario.pos1 == Green | scenario.pos2 == Blue | scenario.pos3 == ${pos3}
    [Arguments]    ${pos1}    ${pos2}    ${pos3}=Orange
    RETURN    ${pos1}    ${pos2}    ${pos3}

Keyword that expands its varargs
    [Documentation]    *model info*
    ...    :MOD: ${varargs}= ${varargs} + [Pink, ${varargs}[0]]
    ...    :IN: scenario.varargs = ${varargs}
    ...    :OUT: if scenario.varargs: scenario.varargs[-1] == scenario.varargs[0] and scenario.varargs[-2] == Pink
    [Arguments]    @{varargs}
    RETURN    @{varargs}

Keyword that expands free named arguments
    [Documentation]    *model info*
    ...    :MOD: ${free}= {**${free}, **dict(colour2=Blue, newcolour=Pink, dupcolour=${free}[colour1])}
    ...    :IN: scenario.free = ${free}
    ...    :OUT: if scenario.free: scenario.free[colour1] == scenario.free[dupcolour] and scenario.free[newcolour] == Pink
    [Arguments]    &{free}
    RETURN    &{free}

Keyword with all ${emb_arg} argument styles mixed
    [Documentation]    *model info*
    ...    :MOD: ${emb_arg}= [Green] | ${pos1}= [Green, Blue] | ${pos2}= [Green, Blue]
    ...          ${named1}= [Green, Blue] | ${named2}= [Green, Blue]
    ...          ${varargs}= ${varargs} + [Pink, ${varargs}[0]]
    ...          ${free}= {**${free}, **dict(colour2=Blue, newcolour=Pink, dupcolour=${free}[colour1])}
    ...    :IN: scenario.emb = ${emb_arg}
    ...         scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2}
    ...         scenario.named1 = ${named1} | scenario.named2 = ${named2}
    ...         scenario.varargs = ${varargs} | scenario.free = ${free}
    ...    :OUT: scenario.emb == Green
    ...          scenario.pos1 == Green | scenario.pos2 == Blue
    ...          scenario.named1 == Orange | scenario.named2 == Green
    ...          if scenario.varargs: scenario.varargs[-1] == scenario.varargs[0] and scenario.varargs[-2] == Pink
    ...          if scenario.free: scenario.free[colour1] == scenario.free[dupcolour] and scenario.free[newcolour] == Pink
    [Arguments]    ${pos1}    ${pos2}    @{varargs}    ${named1}=Orange    ${named2}    &{free}
    VAR    &{all_args}=    emb=${emb_arg}    pos1=${pos1}    pos2=${pos2}    named1=${named1}    named2=${named2}
    ...                    varargs=${varargs}    &{free}
    RETURN    ${all_args}
