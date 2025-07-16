*** Settings ***
Documentation     Contrary to action keywords, bahviour driven steps are expected to be at the
...               center of your modelling. Steps starting with any of the bdd prefixes that do
...               not have modeling info will be rejected.
Suite Setup       Run keyword and expect error    Model info incomplete for step: When Log    Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Keyword without model info as bdd step should fail
    Pass execution    Accepting intentionally unexecutable scenario
    Buy a birthday card
    When Log    Now there is a blank birthday card
    Write name 'Johan' on the birthday card
