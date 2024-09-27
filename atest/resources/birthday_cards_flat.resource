*** Keywords ***
'${person}' buys a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card | birthday_card.with_whom = ${person}
    Log    choosing a birthday card with baloons
    Set suite variable    ${has_card}    ${person}
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

'${person}' has the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.with_whom == ${person}
    ...    :OUT: birthday_card.with_whom == ${person}
    Log    The card is right here in ${person}'s hand
    Should be equal    ${has_card}    ${person}

'${person}' writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${person})
    Log    Writing '${person}' on the birthday card
    Set suite variable    @{names}    @{names}    ${person}

the birthday card has '${name}' written on it
    [Documentation]    *model info*
    ...    :IN: ${name} in birthday_card.names
    ...    :OUT: ${name} in birthday_card.names
    Should contain    ${names}    ${name}

the birthday card does not have '${name}' written on it
    [Documentation]    *model info*
    ...    :IN: ${name} not in birthday_card.names
    ...    :OUT: ${name} not in birthday_card.names
    Should not contain    ${names}    ${name}

the birthday card has ${n} name${plural} written on it
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) == ${n}
    ...    :OUT: len(birthday_card.names) == ${n}
    Length should be    ${names}    ${{int(${n})}}

'${person A}' passes the birthday card ${back/on} to '${person B}'
    [Documentation]    *model info*
    ...    :IN: birthday_card.with_whom == ${person A}
    ...    :OUT: birthday_card.with_whom = ${person B}
    Log    Here you go ${person B}
    Log    Thank you ${person A}, I'll be sure to put name on here.
    Set suite variable    ${has_card}    ${person B}

'${person}' refuses to write their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card
    No operation
