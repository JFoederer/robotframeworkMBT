*** Keywords ***
a blank Birthday card
    Log    choosing a birthday card with baloons
    @{names}=    Create list
    Set suite variable    ${names}

model a blank Birthday card
    Set Model preconditions    None
    Set Model postconditions    new birthday_card    birthday_card.names \= []

'${name}' writes their name on the birthday card
    Log    Writing '${name}' on the birthday card
    Set suite variable    @{names}    @{names}    ${name}

model '${name}' writes their name on the birthday card
    Set Model preconditions    birthday_card
    Set Model postconditions    birthday_card.names.append \= [${name}]

the birthday card has '${name}' written on it
    Should Contain    ${names}    ${name}

model the birthday card has '${name}' written on it
    Set Model preconditions    None
    Set model postconditions    None
