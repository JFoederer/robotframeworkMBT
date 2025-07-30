*** Keywords ***
Buy a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card | birthday_card.names=[]
    Log    choosing a birthday card with baloons
    @{names}=    Create list
    Set suite variable    ${names}

Write name '${name}' on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name})
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

Names written on the birthday card
    [Documentation]    *model info*
    ...    :IN: new modelcheck | modelcheck.in_condition = birthday_card.names[0]
    ...    :OUT: modelcheck.out_condition = birthday_card.names[-1]
    RETURN    ${names}

Extra check on ${var} and model info
    [Arguments]    ${first}    ${last}
    [Documentation]    *model info*
    ...    :IN: modelcheck.in_condition == ${first} | modelcheck.out_condition == ${last}
    ...    :OUT: del modelcheck
    Should Contain    ${var}    ${first}
    Should Contain    ${var}    ${last}

Number of names written on the birthday card
    ${length}=    Get length    ${names}
    RETURN    ${length}

Writing the birthday card
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) == 0
    ...    :OUT: len(birthday_card.names) == 2
    ${n_names}=    Get length    ${names}
    Should Be Equal    ${n_names}    ${2}
