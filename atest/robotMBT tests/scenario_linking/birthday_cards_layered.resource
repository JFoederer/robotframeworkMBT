*** Settings ***
Resource          birthday_cards_common.resource

*** Keywords ***
'${name}' writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: ${name} in birthday_card.names
    Should Contain    ${names}    ${name}

'${name}' writes their name in pen on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name}) | birthday_card.style = pen
    Log    ${name} prefers to use a pen for writing
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}
    Set suite variable    ${writing style}    ink

'${name}' is written in ink on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card.style == pen | ${name} in birthday_card.names
    ...    :OUT: birthday_card.style == pen | ${name} in birthday_card.names
    Should be equal    ${writing style}    ink
