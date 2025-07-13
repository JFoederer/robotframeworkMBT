*** Settings ***
Documentation     Contrary to action keywords, bahviour driven steps are expected to be at the
...               center of your modelling. Steps starting with any of the bdd prefixes that do
...               not have modeling info will be rejected.
Suite Setup       Run keyword and expect error    Model info incomplete for step: When Log    Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Keyword without model info as bdd step should fail
    Pass execution    Accepting intentionally unexecutable scenario
    Johan buys a birthday card
    When Log    Now there is a blank birthday card
    Johan writes their name on the birthday card
    The birthday card has 'Johan' written on it
