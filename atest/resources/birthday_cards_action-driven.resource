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

Write name '${name}' on the birthday card (with modifer)
    [Documentation]    *model info*
    ...    :MOD: ${name}= [name for name in (Johan, Frederique) if name not in birthday_card.names]
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name})
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

Write ${name} as third unique name on the birthday card
    [Documentation]    *model info*
    ...    :IN: len(set(birthday_card.names)) == 2 | ${name} not in birthday_card.names
    ...    :OUT: birthday_card.names.append(${name})
    Set suite variable    @{names}    @{names}    ${name}

Names written on the birthday card
    [Documentation]    *model info*
    ...    :IN: new modelcheck | modelcheck.in_condition = birthday_card.names[0]
    ...    :OUT: modelcheck.out_condition = birthday_card.names[-1]
    ...
    ...    The model info in this step is used to refer to the :IN: and :OUT: expressions
    ...    explicitely to confirm proper processing. It has no meaning for the scenarios.
    RETURN    ${names}

Extra check on ${var} and model info
    [Arguments]    ${first}    ${last}
    [Documentation]    *model info*
    ...    :IN: modelcheck.in_condition == ${first} | modelcheck.out_condition == ${last}
    ...    :OUT: del modelcheck
    Should contain    ${var}    ${first}
    Should contain    ${var}    ${last}

Number of names written on the birthday card
    [Documentation]    Deliberately unmodelled
    ${length}=    Get length    ${names}
    RETURN    ${length}

Writing the birthday card
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) == 0
    ...    :OUT: len(birthday_card.names) == 2
    ${n_names}=    Get length    ${names}
    Should be equal    ${n_names}    ${2}
