*** Settings ***
Library    String

*** Keywords ***
buying a birthday card
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new birthday_card | birthday_card.names=[]
    Log    choosing a birthday card with baloons
    @{names}=    Create list
    Set suite variable    ${names}

there is a blank Birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.names==[]
    ...    :OUT: birthday_card.names==[]
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

'${name}' is written on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: ${name} in birthday_card.names
    Should Contain    ${names}    ${name}

there is text added in ${style} on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.style == ${style}
    ...    :OUT: birthday_card.style == ${style}
    Should be equal    ${writing style}    ${style}

'${name}' writes their name in pen on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name}) | birthday_card.style = ink
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}
    Log    ${name} prefers to use a pen for writing
    Set suite variable    ${writing style}    ink

'${name}' writes their first letter as a piece of art
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new artwork | artwork.name=${name}[0]
    ...          birthday_card.style = calligraphy
    ${first_letter}=    Get substring    ${name}    0    0
    Log    ${name} writes a beautiful capital letter ${first_letter}

'${name}' writes the other letters in decorative writing
    [Documentation]    *model info*
    ...    :IN: artwork.name
    ...    :OUT: artwork.name+=${name}[1:] | birthday_card.names.append(artwork.name)
    ...          birthday_card.style = calligraphy
    ${other_letters}=    Get substring    ${name}    1
    Log    ${name} writes ${other_letters} in a matching font
    Set suite variable    @{names}    @{names}    ${name}
    Log    ${name} prefers to use a pen for writing
    Set suite variable    ${writing style}    calligraphy

'${name}' writes their name in pencil on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card | new _pencil
    ...    :OUT: _pencil.tip==sharp | birthday_card.names.append(${name})
    ...          birthday_card.style = pencil
    Set suite variable    @{names}    @{names}    ${name}
    Log    ${name} prefers to use a pencil for writing
    Set suite variable    ${writing style}    pencil

a pencil is needed for writing
    [Documentation]    *model info*
    ...    :IN: _pencil
    ...    :OUT: _pencil
    Log    Found a pencil! But you might want to check it...

the pencil has a broken tip
    [Documentation]    *model info*
    ...    :IN:  _pencil.tip=broken
    ...    :OUT: _pencil.tip=broken
    Log    Oh no, I can't write like this :-(

the tip of the pencil is sharpend
    [Documentation]    *model info*
    ...    :IN: _pencil.tip==broken
    ...    :OUT: _pencil.tip=sharp
    Log    Nice and sharp again

the pencil is ready for writing
    [Documentation]    *model info*
    ...    :IN: _pencil.tip==sharp
    ...    :OUT: _pencil.tip==sharp
    Log    I can work with this

'${writer}' writes ${recepient}'s address on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.recepient = ${recepient}
    Log    Writing ${recepient}'s name and address on the card

'${name}' puts the birthday card in the mail
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.is_mailed = True
    Log    put it in the mailbox

a birthday card for ${recepient} was put in the mail
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_mailed | birthday_card.recepient == ${recepient}
    ...    :OUT: birthday_card.is_mailed | birthday_card.recepient == ${recepient}
    Log    a birthday card for ${recepient} was put in the mail

the birthcard is is delivered to ${recepient}'s mailbox
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_mailed
    ...    :OUT: birthday_card.is_delivered = True | birthday_card.mailbox = ${recepient}
    Log    Something fell on the doormat

'${name}' received the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.is_delivered == True | birthday_card.mailbox == ${name}
    ...    :OUT: birthday_card.is_delivered == True | birthday_card.mailbox == ${name}
    Log    Something fell on ${name}'s doormat
