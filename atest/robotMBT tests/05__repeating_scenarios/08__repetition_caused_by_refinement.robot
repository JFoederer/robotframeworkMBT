*** Settings ***
Documentation     This suite has more low-level scenarios than high-level scenarios,
...               meaning that the high-level scenario must be repeated in order for
...               the second low-level scenario to be reached.
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

low-level scenario A
    Given there is a birthday card
    when Someone writes their name in pen on the birthday card
    then the birthday card has 'Someone' written on it
    and there is text added in ink on the birthday card

low-level scenario B
    Given there is a birthday card
    when Someone writes their name in pen on the birthday card
    then the birthday card has 'Someone' written on it
    and there is text added in ink on the birthday card
