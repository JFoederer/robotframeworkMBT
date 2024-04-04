*** Settings ***
Documentation     This suite demonstrates step refinement in its simplest form. There are
...               two scenarios. One scenario can be considered high-level, the other
...               low-level. The high-level scenario contains a _WHEN_ step that is not
...               directly executable. The low-level scenario acts as step refinement to
...               implement the concrete steps needed to satisfy the expected result of
...               the _WHEN_ step. For this to be successful, the _WHEN_ step from the
...               high-level scenario must match the _GIVEN_ step of the refinement
...               scenario.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_composed.resource
Library           robotmbt

*** Test Cases ***
high-level scenario
    Given there is a blank birthday card available
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it

low-level scenario
    Given there is a birthday card
    when 'Johan' writes their name in pen on the birthday card
    then the birthday card has 'Johan' written on it
    and there is text added in ink on the birthday card

leading scenario
    When 'Johan' buys a birthday card
    then there is a blank birthday card available
