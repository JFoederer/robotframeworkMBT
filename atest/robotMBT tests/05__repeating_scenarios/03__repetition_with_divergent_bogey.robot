*** Settings ***
Documentation     The divergent bogey suite is similar to the identity bogey suite in
...               that it contains a scenario that can be repeated indefinitely. The
...               difference is that inserting the repeating scenario at the wrong time
...               will cause the model to keep growing without ever reaching the entry
...               condition for the other scenario.
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

Being the first to write on the card
    Given there is a blank birthday card available
    when 'Johan' writes their name on the birthday card
    then the birthday card has 1 name written on it

At least 4 people can write their name on the card
    Given the birthday card has 3 names written on it
    when 'Someone' writes their name on the birthday card
    then the birthday card has 4 names written on it
