*** Settings ***
Documentation     In action-driven testing it is more common to use variables. Variables can be
...               assigned during a scenario from the return value of a keyword, as seen before, or
...               by using Robot's VAR systax. This test checks the VAR syntax for scalars and
...               multi-value types.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Variable definition using Robot's VAR syntax
    Buy a birthday card
    Write name 'Johan' on the birthday card
    Write name 'Frederique' on the birthday card
    ${n_names}=    Number of names written on the birthday card
    VAR    ${two}=    ${2}
    Should be equal    ${n_names}    ${two}
    @{actual names}=    Names written on the birthday card
    VAR    @{expected names}=    Johan    Frederique
    Should be equal    ${actual names}    ${expected names}
