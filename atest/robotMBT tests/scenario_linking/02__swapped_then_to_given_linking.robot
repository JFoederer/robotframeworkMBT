*** Settings ***
Documentation     This test suite demonstrates direct one-on-one linking of scenarios.
...               The _THEN_ from one scenario matches exactly to the _GIVEN_ of the
...               other scenario. Because the scenarios are listed in the test suite in
...               reverse order, this test suite would fail in a regular Robot Framework
...               test run. It passes when the model figures out the dependency between
...               the test cases and swaps their order.
Suite Setup       Treat this test suite Model-based
Resource          birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
trailing scenario
    Given there is a blank Birthday card
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it

leading scenario
    When Johan buys a birthday card
    then there is a blank birthday card
