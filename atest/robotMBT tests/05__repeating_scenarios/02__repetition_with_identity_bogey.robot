*** Settings ***
Documentation     This suite includes an identity scenario, meaning that it leaves the
...               model unchanged. It can act as a decoy when permitting repeated
...               scenarios, because it can be inserted indefinitely, without ever
...               reaching the next step in coverage.
Suite Setup       Enter test suite
Suite Teardown    Should be equal    ${test_count}    ${5}
Test Teardown     Increase test count
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

Refusing to share the birthday card
    Given there is a birthday card
    and the birthday card has 'Someone' written on it
    when Johan refuses to write their name on the birthday card
    then the birthday card has 'Someone' written on it
    but the birthday card does not have 'Johan' written on it

At least 3 people can write their name on the card
    Given the birthday card has 2 names written on it
    when someone writes their name on the birthday card
    then the birthday card has 3 names written on it

*** Keywords ***
Enter test suite
    Set Suite Variable    ${test_count}    ${0}
    Treat this test suite Model-based

Increase test count
    Set suite variable    ${test_count}    ${test_count+1}
