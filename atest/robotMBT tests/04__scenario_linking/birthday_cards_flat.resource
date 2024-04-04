*** Settings ***
Resource          birthday_cards_common.resource

*** Keywords ***
'${name}' writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: birthday_card
    ...    :OUT: birthday_card.names.append(${name})
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}
