*** Settings ***
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When 'Johan' buys a birthday card
    then there is a blank birthday card available
    and 'Johan' has the birthday card

Johan writes their name on the card
    Given 'Johan' has the birthday card
    and the birthday card does not have 'Johan' written on it
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it

Passing the card on to someone else
    Given 'Johan' has the birthday card
    when 'Johan' passes the birthday card on to 'Someone else'
    then 'Someone else' has the birthday card

Someone else writes their name on the card
    Given 'Someone else' has the birthday card
    when 'Someone else' writes their name on the birthday card
    and 'Someone else' passes the birthday card back to 'Johan'
    then the birthday card has 'Someone else' written on it
    and 'Johan' has the birthday card

At least 4 people can write their name on the card
    Given the birthday card has 3 names written on it
    when 'Tannaz' writes their name on the birthday card
    then the birthday card has 4 names written on it
