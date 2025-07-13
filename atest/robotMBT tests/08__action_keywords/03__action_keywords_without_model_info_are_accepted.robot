*** Settings ***
Documentation     Not all keywords are under your own control, like Robot Framework's BuiltIn
...               keywords. In this test the BuiltIn keyword Log is used to prove that action
...               keywords can be used without model info. These keywords will not affect the
...               model.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Action-driven scenario with BuiltIn keyword
    Johan buys a birthday card
    Log    Now there is a blank birthday card
    Johan writes their name on the birthday card
    The birthday card has 'Johan' written on it
