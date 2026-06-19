*** Settings ***
Documentation     This test suite confirms that a time target can stop a test run if it is the
...               last condition to be satisfied. For run duration reasons an unrealistically
...               short time span is used, while all other conditions are disabled. This has a
...               double effect. One effect is that the test run should always stop after the
...               first test case, even though a longer trace was created. We know that a longer
...               trace was created due to the second effect. With the coverage target disabled
...               the coverage drought limit does not kick in, so it is also the time target that
...               is responsible for stopping the trace generation without getting stuck in an
...               infinite loop.
Suite Setup       Treat this test suite Model-based    coverage_target=0    time_target=0.1 sec
Suite Teardown    Should be equal    ${scenario_count}    ${1}
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
