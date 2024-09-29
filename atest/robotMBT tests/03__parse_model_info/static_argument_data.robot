*** Settings ***
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
leading scenario
    When 'Johan' buys a birthday card
    then there is a blank birthday card available

simple argument
    Given there is a birthday card
    when 'Gertjan' writes their name on the birthday card
    then the birthday card has 'Gertjan' written on it

argument data is case sensitive
    Given there is a birthday card
    when 'GertJan' writes their name on the birthday card
    then the birthday card has 'GertJan' written on it
    but the birthday card does not have 'GERTJAN' written on it

argument with spaces
    Given there is a birthday card
    when 'Gert Jan' writes their name on the birthday card
    then the birthday card has 'Gert Jan' written on it

argument with Python operator
    Given there is a birthday card
    when 'Gert-Jan' writes their name on the birthday card
    then the birthday card has 'Gert-Jan' written on it

argument with apostrophe
    Given there is a birthday card
    when 'Jeanne d'Arc' writes their name on the birthday card
    then the birthday card has 'Jeanne d'Arc' written on it

argument in unicode
    Given there is a birthday card
    when '藤原拓海' writes their name on the birthday card
    then the birthday card has '藤原拓海' written on it

argument with Python builtin function
    Given there is a birthday card
    when 'max' writes their name on the birthday card
    then the birthday card has 'max' written on it

argument with Python keyword
    Given there is a birthday card
    when 'elif' writes their name on the birthday card
    then the birthday card has 'elif' written on it

argument used as name in model
    When a user introduces Birthday card as new domain term to the model
    Then domain term Birthday card is accessible from the model
    and property illustration design is set to birthday cake for domain term Birthday card

*** Keywords ***
a user introduces ${term} as new domain term to the model
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new ${term}
    No operation

domain term ${term} is accessible from the model
    [Documentation]    *model info*
    ...    :IN: ${term}.accessible == True
    ...    :OUT: ${term}.accessible = True
    No operation

property ${property} is set to ${value} for domain term ${term}
    [Documentation]    *model info*
    ...    :IN: ${term}.${property} == ${value}
    ...    :OUT: ${term}.${property} = ${value}
    No operation
