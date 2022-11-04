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

'${name}' writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: ${name} in birthday_card.names
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

'${name}' writes their name in pen on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name})
    Log    ${name} prefers to use a pen for writing
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

'${name}' writes their first letter as a piece of art
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new calligraphy | calligraphy.name=${name}[0]
    ${first_letter}=    Get substring    ${name}    0    0
    Log    ${name} writes a beautiful capital letter ${first_letter}

'${name}' writes the other letters in decorative writing
    [Documentation]    *model info*
    ...    :IN: calligraphy.name
    ...    :OUT: calligraphy.name+=${name}[1:] | birthday_card.names.append(calligraphy.name)
    ${other_letters}=    Get substring    ${name}    1
    Log    ${name} writes ${other_letters} in a matching font
    Set suite variable    @{names}    @{names}    ${name}

'${name}' is written as calligraphy on the birthday card
    [Documentation]    *model info*
    ...    :IN: calligraphy.name == ${name} | calligraphy.name in birthday_card.names
    ...    :OUT: calligraphy.name == ${name} | calligraphy.name in birthday_card.names
    Should Contain    ${names}    ${name}

'${name}' writes their name in pencil on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: pencil.tip==sharp | birthday_card.names.append(${name})
    Set suite variable    @{names}    @{names}    ${name}

there is a pencil available
    [Documentation]    *model info*
    ...    :IN: new pencil | pencil.tip=broken
    ...    :OUT: pencil.tip==broken
    Log    Found a pencil! But you might want to check it...

the pencil has a broken tip
    [Documentation]    *model info*
    ...    :IN:  pencil.tip==broken
    ...    :OUT: pencil.tip==broken
    Log    Oh no, I can't write like this :-(

the tip of the pencil is sharpend
    [Documentation]    *model info*
    ...    :IN: pencil.tip==broken
    ...    :OUT: pencil.tip=sharp
    Log    Nice and sharp

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
