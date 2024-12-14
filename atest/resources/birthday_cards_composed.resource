*** Settings ***
Library    String

*** Keywords ***
${person} buys a birthday card
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
    Log    The card has balloons on the front, but the inside looks a bit empy

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

${person} writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card | scenario.count = len(birthday_card.names)
    ...    :OUT: ${person} in birthday_card.names
    ...          len(birthday_card.names) == scenario.count+1
    Should Contain    ${names}    ${person}

the birthday card has ${n} name${plural} written on it
    [Documentation]    *model info*
    ...    :IN: len(birthday_card.names) == ${n}
    ...    :OUT: len(birthday_card.names) == ${n}
    Length should be    ${names}    ${{int(${n})}}

there is text added in ${style} on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.style == ${style}
    ...    :OUT: birthday_card.style == ${style}
    Should be equal    ${writing style}    ${style}

${person} writes their name in pen on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card | scenario.count
    ...    :OUT: birthday_card.names.append(${person}) | birthday_card.style = ink
    ...
    ...    Using scenario data is a trick to force this step into a refinement
    Log    Writing '${person}' on the birthday card
    Set suite variable    @{names}    @{names}    ${person}
    Log    ${person} prefers to use a pen for writing
    Set suite variable    ${writing style}    ink

${person} writes their first letter as a piece of art
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: scenario.artwork = ${person}[0]
    ...          birthday_card.style = calligraphy
    ${first_letter}=    Get substring    ${person}    0    0
    Log    ${person} writes a beautiful capital letter ${first_letter}

${person} writes the other letters in decorative writing
    [Documentation]    *model info*
    ...    :IN: scenario.artwork
    ...    :OUT: scenario.artwork+=${person}[1:] | birthday_card.names.append(scenario.artwork)
    ...          birthday_card.style = calligraphy
    ${other_letters}=    Get substring    ${person}    1
    Log    ${person} writes ${other_letters} in a matching font
    Set suite variable    @{names}    @{names}    ${person}
    Log    ${person} prefers to use a pen for writing
    Set suite variable    ${writing style}    calligraphy

${person} writes their name in pencil on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card | scenario.pencil=broken
    ...    :OUT: scenario.pencil==sharp | birthday_card.names.append(${person})
    ...          birthday_card.style = pencil
    Set suite variable    @{names}    @{names}    ${person}
    Log    ${person} prefers to use a pencil for writing
    Set suite variable    ${writing style}    pencil

a pencil is needed for writing
    [Documentation]    *model info*
    ...    :IN: scenario.pencil
    ...    :OUT: scenario.pencil
    Log    Found a pencil! But you might want to check it...

the pencil has a broken tip
    [Documentation]    *model info*
    ...    :IN:  scenario.pencil==broken
    ...    :OUT: scenario.pencil=broken
    Log    Oh no, I can't write like this :-(

someone sharpens the tip of the pencil
    [Documentation]    *model info*
    ...    :IN: scenario.pencil==broken
    ...    :OUT: scenario.pencil=sharp
    Log    Nice and sharp again

the pencil is ready for writing
    [Documentation]    *model info*
    ...    :IN: scenario.pencil==sharp
    ...    :OUT: scenario.pencil==sharp
    Log    I can work with this

${sender} writes ${recepient}'s address on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.recepient = ${recepient}
    Log    Writing ${recepient}'s name and address on the card

${person} puts the birthday card in the mail
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.is_mailed = True
    Log    put it in the mailbox

a birthday card for ${recepient} was put in the mail
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_mailed | birthday_card.recepient == ${recepient}
    ...    :OUT: birthday_card.is_mailed | birthday_card.recepient == ${recepient}
    Log    a birthday card for ${recepient} was put in the mail

the postal service delivers the birthday card to ${recepient}'s mailbox
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_mailed
    ...    :OUT: birthday_card.is_delivered = True | birthday_card.mailbox = ${recepient}
    Log    Something fell on the doormat

${person} received the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_delivered == True | birthday_card.mailbox == ${person}
    ...    :OUT: birthday_card.is_delivered == True | birthday_card.mailbox == ${person}
    Log    Something fell on ${person}'s doormat
