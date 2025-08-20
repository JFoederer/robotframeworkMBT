*** Settings ***
Documentation     This test suite takes a single basic birthday card scenario, but uses action
...               keywords rather than bdd steps. Action keywords process their :IN: and : OUT:
...               conditions like when steps, i.e. both :IN: and :OUT: conditions are processed.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Action-driven scenario omitting given-when-then
    Buy a birthday card
    Write name 'Johan' on the birthday card
    Write name 'Frederique' on the birthday card
    ${n_names}=    Number of names written on the birthday card
    Should Be Equal    ${n_names}    ${2}
