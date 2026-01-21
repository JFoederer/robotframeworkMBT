*** Settings ***
Documentation     This suite requires a larger amount of repetitions to reach the final
...               scenario.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

Someone writes their name on the card
    Given there is a birthday card
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it

At least 42 people can write their name on the card
    Given the birthday card has 41 names written on it
    when someone writes their name on the birthday card
    then the birthday card has 42 names written on it
