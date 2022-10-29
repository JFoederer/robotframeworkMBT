*** Settings ***
Resource          birthday_cards_common.resource

*** Keywords ***
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
