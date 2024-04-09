*** Settings ***
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When 'Someone' buys a birthday card
    then there is a blank birthday card available

Someone writes their name on the card
    Given there is a birthday card
    when 'Someone' writes their name on the birthday card
    then the birthday card has 'Someone' written on it

Refusing to share the birthday card
    Given there is a birthday card
    and the birthday card has 'Someone' written on it
    when 'Johan' refuses to write their name on the birthday card
    then the birthday card has 'Someone' written on it
    but the birthday card does not have 'Johan' written on it

At least 3 people can write their name on the card
    Given the birthday card has 2 names written on it
    when 'Someone' writes their name on the birthday card
    then the birthday card has 3 names written on it
