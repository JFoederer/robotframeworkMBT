*** Keywords ***
${person} is having their birthday
    [Documentation]    *model info*
    ...    :IN: new party | party.host = ${person} | party.guests = []
    ...    :OUT: None
    Set suite variable    \${celebrant}    ${person}
    @{guests}=    Create list
    Set suite variable    ${guests}

${guest} is a friend of ${host}
    [Documentation]    *model info*
    ...    :MOD: ${guest}= [${guest}]
    ...    :IN: party.host == ${host} | party.guests.append(${guest})
    ...    :OUT: None
    Set suite variable    @{guests}    @{guests}    ${guest}

${person} buys a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card
    Log    choosing a birthday card with baloons
    Set suite variable    \${has_card}    ${person}
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
    ...    :MOD: ${person}= party.guests
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${person})
    Log    Writing '${person}' on the birthday card
    Set suite variable    @{names}    @{names}    ${person}

${person}'s name is not yet on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${person}= [guest for guest in party.guests if guest not in birthday_card.names]
    ...    :IN: ${person} not in birthday_card.names
    ...    :OUT: ${person} not in birthday_card.names
    Should not contain    ${names}    ${person}

the birthday card has '${name}' written on it
    [Documentation]    *model info*
    ...    :MOD: ${name}= [guest for guest in party.guests if guest in birthday_card.names]
    ...    :IN: ${name} in birthday_card.names
    ...    :OUT: ${name} in birthday_card.names
    Should contain    ${names}    ${name}

the birthday card has ${n} different names written on it
    [Documentation]    *model info*
    ...    :IN: len(set(birthday_card.names)) == ${n}
    ...    :OUT: len(set(birthday_card.names)) == ${n}
    Length should be    ${names}    ${{int(${n})}}

${person} signs the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${person}= [guest for guest in party.guests if guest not in birthday_card.names]
    ...    :IN: ${person} not in birthday_card.names | scenario.guest = ${person}
    ...    :OUT: ${person} in birthday_card.names
    Should contain    ${names}    ${person}

${person} is signing the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${person}= [scenario.guest]
    ...    :IN: ${person} == scenario.guest
    ...    :OUT: ${person} == scenario.guest
    No Operation

the birthday card has a personal touch
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) > 0
    ...    :OUT: len(birthday_card.names) > 0
    ${number_of_names}=    Get Length    ${names}
    Should be True    ${number_of_names} > 0

${person} adds the wish '${wish}' to the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${person}= party.guests
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.wish = ${wish}
    Set Suite Variable    \${birthday_wish}    ${wish}

the birthday card proclaims: ${wish}
    [Documentation]    *model info*
    ...    :IN: birthday_card.wish == ${wish}
    ...    :OUT: birthday_card.wish == ${wish}
    Should be equal    ${birthday_wish}    ${wish}

${person} is the birthday celebrant
    [Documentation]    *model info*
    ...    :MOD: ${person}= [party.host]
    ...    :IN: party.host == ${person}
    ...    :OUT: party.host == ${person}
    Should be equal    ${celebrant}    ${person}

the birthday celebrant's name, ${name}, is written on the card
    [Documentation]    *model info*
    ...    :MOD: ${name}= [party.host]
    ...    :IN: party.host in birthday_card.names
    ...    :OUT: party.host in birthday_card.names
    Should contain    ${names}    ${name}

the birthday celebrant's name, ${name}, is not written on the card
    [Documentation]    *model info*
    ...    :MOD: ${name}= [party.host]
    ...    :IN: party.host not in birthday_card.names
    ...    :OUT: party.host not in birthday_card.names
    Should not contain    ${names}    ${name}

${sender} writes ${recipient}'s address on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${sender}= party.guests | ${recipient}= [party.host]
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.recipient = ${recipient}
    Set suite variable    \${address of}    ${recipient}
    Log    Writing ${recipient}'s name and address on the card

${sender} tries to write ${recipient}'s address on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${sender}= party.guests | ${recipient}= .*
    ...    :IN: birthday_card
    ...    :OUT: None
    IF   '${recipient}' == '${celebrant}'
        Set suite variable    \${address_of}    ${recipient}
        Log    Writing ${recipient}'s name and address on the card
    ELSE
        Set suite variable    \${address_of}    ${empty}
        Log    Getting stopped by a friend
    END

${recipient}'s address is on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${recipient}= [party.host]
    ...    :IN: birthday_card.address == party.host
    ...    :OUT: birthday_card.address = party.host
    Should be equal    ${recipient}    ${celebrant}
    Should be equal    ${address of}    ${celebrant}
    Log    The card is addressed to ${recipient}

${person} alerts ${other person} that it is ${celebrant}'s birthday
    [Documentation]    *model info*
    ...    :MOD: ${person}= party.guests | ${other person}= party.guests | ${celebrant}= [party.host]
    ...    :IN: ${celebrant} == party.host
    ...    :OUT: ${celebrant} == party.host
    Should contain    ${guests}    ${person}
    Should not be equal    ${address of}    ${celebrant}
    Log    Uhm ${other person}? You do relize that it is ${celebrant}'s birthday?

${person} confirms ${recipient}'s address
    [Documentation]    *model info*
    ...    :MOD: ${person}= party.guests | ${recipient}= [party.host]
    ...    :IN: ${recipient} == party.host
    ...    :OUT: ${recipient} == party.host
    Should contain    ${guests}    ${person}
    Should be equal    ${recipient}    ${celebrant}
    Log    Yes, that is correct. This is ${recipient}'s address?
