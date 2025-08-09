*** Settings ***
Documentation     This test suites explores some more detailed cases of argument handling.
Suite Setup       Treat this test suite Model-based
Library           robotmbt

*** Test Cases ***
Escaped argument values
    Keyword with escaped argument values    esc\=assign    this is \${no var}    warning:\t\u26A0

Naming positional agrument
    Comment    Extra check needed to confirm pos2 is kept visable in the kw execution
    Keywword with positional and named arguments    Green    pos2=Red    named1=Blue

Argument with default value
    Keyword with default value    Green    named2=Blue


*** Keywords ***
Keyword with escaped argument values
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2} | scenario.pos3 = ${pos3}
    ...    :OUT: scenario.pos1 == r'esc\=assign'
    ...          scenario.pos2 == r'this is \${no var}'
    ...          scenario.pos3 == 'warning:\t\u26A0'
    ...          scenario.pos3 == 'warning:\t⚠'
    [Arguments]    ${pos1}    ${pos2}    ${pos3}
    Should be equal    ${pos1}    esc\=assign
    Should be equal    ${pos2}    this is \${no var}
    Should be equal    ${pos3}    warning:\t⚠

Keywword with positional and named arguments
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1} | scenario.pos2 = ${pos2} | scenario.named1 = ${named1}
    ...    :OUT: scenario.pos1 == Green | scenario.pos2 == Red | scenario.named1 == Blue
    [Arguments]    ${pos1}    ${pos2}    ${named1}=
    Should be equal    ${pos2}    Red

Keyword with default value
    [Documentation]    *model info*
    ...    :IN: scenario.pos1 = ${pos1} | scenario.named1 = ${named1} | scenario.named2 = ${named2}
    ...    :OUT: scenario.pos1 == Green | scenario.named1 == Red | scenario.named2 == Blue
    [Arguments]    ${pos1}    ${named1}=Red    ${named2}=
    Should be equal    ${named1}    Red
