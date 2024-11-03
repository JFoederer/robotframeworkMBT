*** Keywords ***
${person} is having their birthday
    [Documentation]    *model info*
    ...    :IN: new party | party.host = ${person} | party.guests = []
    ...    :OUT: None
    No Operation

${guest} is a friend of ${host}
    [Documentation]    *model info*
    ...    :IN: party.host == ${host} | party.guests.append(${guest})
    ...    :OUT: None
    No Operation

${person} buys a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card
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

${person} writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card | ${person} = scenario.guest
    ...    :OUT: birthday_card.names.append(${person})
    Log    Writing '${person}' on the birthday card
    Set suite variable    @{names}    @{names}    ${person}

${person}'s name is not yet on the birthday card
    [Documentation]    *model info*
    ...    :IN: ${person} not in birthday_card.names | ${person}= [guest for guest in party.guests if guest not in birthday_card.names][0]
    ...    new scenario | scenario.guest = ${person}
    ...    :OUT: ${person} not in birthday_card.names
    Should not contain    ${names}    ${person}

the birthday card has '${name}' written on it
    [Documentation]    *model info*
    ...    :IN: ${name} in birthday_card.names
    ...    :OUT: ${name}= scenario.guest | scenario.guest in birthday_card.names | del scenario
    Should contain    ${names}    ${name}

the birthday card has ${n} different names written on it
    [Documentation]    *model info*
    ...    :IN: len(set(birthday_card.names)) == ${n}
    ...    :OUT: len(set(birthday_card.names)) == ${n}
    Length should be    ${names}    ${{int(${n})}}
