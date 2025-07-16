*** Settings ***
Documentation     Action keywords process their :IN: and : OUT: conditions like when steps, i.e.
...               both :IN: and :OUT: conditions are processed.. The way this scenario is
...               constructed works because the first keyword has condition :IN: None and creates
...               the birthday card domain term in its :OUT: condition. This satisfies the :IN:
...               condition for the second keyword, making it a valid scenario.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Dependent action keyword can start after setting precondition
    Buy a birthday card
    Write name 'Johan' on the birthday card
