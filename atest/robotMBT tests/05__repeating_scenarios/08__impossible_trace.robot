*** Settings ***
Documentation     This suite contains a scenario that can be repeated indefinitely, but
...               doing so will not get you any closer to the final scenario. The model
...               should detect that this is a lost cause and report this to the user.
Suite Setup       Expect failing suite processing
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

Refusing to sign the birthday card
    Given there is a birthday card
    when everybody refuses to write their name on the birthday card
    then the birthday card has 0 names written on it

At least 42 people can write their name on the card
    Skip when unreachable
    Given the birthday card has 41 names written on it
    when someone writes their name on the birthday card
    then the birthday card has 42 names written on it

*** Keywords ***
Expect failing suite processing
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Run keyword and expect error    Unable to compose*    Treat this test suite Model-based
    Set suite variable    ${expected_error_detected}    ${True}

Skip when unreachable
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    ...
    ...    If the scenario is inserted after proper detection of the expected error,
    ...    then this keyword causes the remainder of the scenario to be skipped and
    ...    the test passes. When inserted without detected error, the scenario will
    ...    fail.
    IF    ${expected_error_detected}
        Pass execution    Accepting intentionally unreachable scenario
    END
