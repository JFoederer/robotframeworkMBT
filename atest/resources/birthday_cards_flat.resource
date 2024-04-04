*** Keywords ***
someone buys a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card
    Log    choosing a birthday card with baloons
    @{names}=    Create list
    Set suite variable    ${names}

there is a blank birthday card available
    [Documentation]    *model info*
    ...    :IN: birthday_card.names==[]
    ...    :OUT: birthday_card.names=[]
    Length should be    ${names}    0

there is a birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card
    Variable should exist    ${names}

'${name}' writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name})
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

the birthday card has '${name}' written on it
    [Documentation]    *model info*
    ...    :IN: ${name} in birthday_card.names
    ...    :OUT: ${name} in birthday_card.names
    Should Contain    ${names}    ${name}

the birthday card has ${n} name${plural} written on it
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) == ${n}
    ...    :OUT: len(birthday_card.names) == ${n}
    Length should be    ${names}    ${{int(${n})}}
