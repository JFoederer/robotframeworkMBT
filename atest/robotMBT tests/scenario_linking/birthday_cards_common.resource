*** Keywords ***
a blank Birthday card
    [Documentation]    *model info*
    ...    :IN: new birthday_card | birthday_card.names=[]
    ...    :OUT: None
    Log    choosing a birthday card with baloons
    @{names}=    Create list
    Set suite variable    ${names}

there is a birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card
    Variable should exist    ${names}

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
