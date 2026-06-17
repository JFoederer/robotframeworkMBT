*** Settings ***
Documentation     At single coverage (the default), the final suite should repeat the middle
...               exactly once, then insert the last scenario and stop.
Suite Setup       Treat this test suite Model-based
Suite Teardown    Should be equal    ${scenario_count}    ${4}
Test Teardown     Set suite variable    ${scenario_count}    ${scenario_count+1}
Resource          ../../../resources/birthday_cards_flat.resource
Library           robotmbt

*** variables ***
${scenario_count}    ${0}

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
