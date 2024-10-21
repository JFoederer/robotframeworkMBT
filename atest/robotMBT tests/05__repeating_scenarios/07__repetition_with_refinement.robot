*** Settings ***
Documentation     This suite is similar to the Single repetition scenario, but
...               with the difference that this time the repeated scenario has
...               a step that requires refinement.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_composed.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

high-level scenario
    Given there is a birthday card
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it

low-level scenario
    Given there is a birthday card
    when Someone writes their name in pen on the birthday card
    then the birthday card has 'Someone' written on it
    and there is text added in ink on the birthday card

At least 3 people can write their name on the card
    Given the birthday card has 2 names written on it
    when Someone writes their name on the birthday card
    then the birthday card has 3 names written on it
