*** Settings ***
Documentation     This suite confirms that a scenario that can be inserted at the place
...               of refinement based on its entry conditions, but afterwards does not
...               satisfy the high-level scenario's exit conditions, is rejected.
Suite Setup       Expect failing suite processing
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt


*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

high-level scenario
    Given there is a birthday card
    when Two people write their name on the birthday card
    then the birthday card has 2 names written on it

low-level scenario
    Given there is a birthday card
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it


*** Keywords ***
Two people write their name on the birthday card
    [Documentation]
    ...    *model info*
    ...    :IN: scenario.count = len(birthday_card.names)
    ...    :OUT: len(birthday_card.names) == scenario.count+2
    Skip when unreachable
    Length should be    ${names}    ${2}

Expect failing suite processing
    Run keyword and expect error    Unable to compose*    Treat this test suite Model-based
    Set suite variable    ${expected_error_detected}    ${True}

Skip when unreachable
    [Documentation]
    ...    If the scenario is inserted after proper detection of the expected error,
    ...    then this keyword causes the remainder of the scenario to be skipped and
    ...    the test passes. When inserted without detected error, the scenario will
    ...    fail.
    IF    ${expected_error_detected}
        Pass execution    Accepting intentionally unreachable scenario
    END
