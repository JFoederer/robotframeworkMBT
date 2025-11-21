*** Settings ***
Documentation     This test suite demonstrates direct one-on-one linking of scenarios.
...               The _THEN_ from the leading scenario matches exactly to the _GIVEN_ of
...               the trailing scenario.
...
...               Note that this test suite would also pass when run in Robot Framework without additional processing.
Suite Setup       Treat this test suite Model-based  graph=scenario
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
leading scenario
    When Johan buys a birthday card
    then there is a blank birthday card available

trailing scenario
    Given there is a blank birthday card available
    when Johan writes their name on the birthday card
    then the birthday card has 'Johan' written on it
