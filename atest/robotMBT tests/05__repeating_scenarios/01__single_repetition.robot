*** Settings ***
Documentation     This suite consists of 3 scenarios. After inserting the leading
...               scenario, the trailing scenario cannot be reached, unless the middle
...               scenario is inserted twice.
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

At least 3 people can write their name on the card
    Given the birthday card has 2 names written on it
    when someone writes their name on the birthday card
    then the birthday card has 3 names written on it
