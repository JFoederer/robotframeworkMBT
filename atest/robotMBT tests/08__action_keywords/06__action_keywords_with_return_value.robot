*** Settings ***
Documentation     In 'classical' action-driven testing it is common to have keywords return data to
...               the test case that is then stored in a variable. This test case confirms that
...               variables van be used and that the model info from assignment steps is
...               processed.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Keyword with return value and model info
    Buy a birthday card
    Write name 'Johan' on the birthday card
    Write name 'Frederique' on the birthday card
    ${name list}=    Names written on the birthday card
    Extra check on ${name list} and model info    Johan    Frederique
