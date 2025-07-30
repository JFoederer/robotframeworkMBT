*** Settings ***
Documentation     The divergent bogey suite is similar to the identity bogey suite in
...               that it contains a scenario that can be repeated indefinitely. The
...               difference is that inserting the repeating scenario at the wrong time
...               will cause the model to keep growing without ever reaching the entry
...               condition for the other scenario.
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

Being the first to write on the card
    Given there is a blank birthday card available
    when Johan writes their name on the birthday card
    then the birthday card has 1 name written on it

At least 4 people can write their name on the card
    Given the birthday card has 3 names written on it
    when someone writes their name on the birthday card
    then the birthday card has 4 names written on it

*** Keywords ***
Enter test suite
    Set Suite Variable    ${test_count}    ${0}
    Treat this test suite Model-based

Increase test count
    Set suite variable    ${test_count}    ${test_count+1}
