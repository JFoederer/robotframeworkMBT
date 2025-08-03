*** Settings ***
Documentation     This suite uses the action-driven format and focuses on step modifiers and
...               repeating scenarios. The last scenario expects three different names on the
...               birthday card, but there is only one scenario writing and that writes only a
...               single name. For this suite to complete, the write scenario must be inserted
...               twice using a different name each time.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
A birthday card is blank after purchase
    Buy a birthday card
    ${n_names}=    Number of names written on the birthday card
    Should be equal    ${n_names}    ${0}

People can write their name on the birthday card
    ${n_names_before}=    Number of names written on the birthday card
    Write name 'Frederique' on the birthday card (with modifer)
    ${n_names_after}=    Number of names written on the birthday card
    Should be equal    ${n_names_before+1}    ${n_names_after}

Multiple people can write their name on the birthday card
    Write Tannaz as third unique name on the birthday card
    ${all_names}=    Names written on the birthday card
    Should contain x times    ${all_names}    Frederique    1
    Should contain x times    ${all_names}    Johan         1
    Should contain x times    ${all_names}    Tannaz        1
