*** Settings ***
Documentation     This test suite combines two action-driven scenarios. The scenarios are
...               listed in reverse order, so the trace generation must put them in the
...               correct order for them to pass.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
trailing scenario
    Write name 'Frederique' on the birthday card
    ${n_names}=    Number of names written on the birthday card
    Should Be Equal    ${n_names}    ${2}

leading scenario
    Buy a birthday card
    Write name 'Johan' on the birthday card
    ${n_names}=    Number of names written on the birthday card
    Should Be Equal    ${n_names}    ${1}
