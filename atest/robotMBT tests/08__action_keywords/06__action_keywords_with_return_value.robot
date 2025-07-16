*** Settings ***
Documentation     This test suite takes a single basic birthday card scenario, but uses the step
...               definitions previously used as given-when-then steps for action-driven testing
...               instead. Action keywords process their :IN: and : OUT: conditions like when
...               steps. The way this scenario is constructed works because the first keyword
...               has :IN: None, the second was already constructed as a when-step and the last
...               keyword has the same condition for both the :IN: and the : OUT: conditions.
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
