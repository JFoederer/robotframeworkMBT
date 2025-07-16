*** Settings ***
Documentation     Not all keywords are under your own control, like Robot Framework's BuiltIn
...               keywords. In this test the BuiltIn keyword Log is used to prove that action
...               keywords can be used without model info. These keywords will not affect the
...               model.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Action-driven scenario with BuiltIn keyword
    Buy a birthday card
    Log    Now there is a blank birthday card
    Write name 'Johan' on the birthday card
