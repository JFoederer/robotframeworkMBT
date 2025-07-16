*** Settings ***
Documentation     This test suite applies refinement to an action keyword. The higher level keyword
...               'Writing the birthday card' is implemented with contradicting :IN: and :OUT:
...               conditions to trigger refinement. The :IN: condition expects a blank birthday
...               card, the :OUT: condition expects 2 names on it. The second scenario fills
...               exactly this gap.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Action keyword with refinement scenario
    Buy a birthday card
    Writing the birthday card
    ${n_names}=    Number of names written on the birthday card
    Should Be Equal    ${n_names}    ${2}

Writing 2 names on the birthday card
    Write name 'Johan' on the birthday card
    Write name 'Frederique' on the birthday card
