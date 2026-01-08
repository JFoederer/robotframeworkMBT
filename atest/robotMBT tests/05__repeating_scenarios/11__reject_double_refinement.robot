*** Settings ***
Documentation     This suite covers a special case where an incomplete rollback inside a
...               scenario which is split up for refinement, could cause two scenarios
...               to be inserted for a single refinement. To get into that situation the
...               high-level scenario has two steps that require refinement. The first
...               one only checks that a certain name is inserted, it does not check the
...               number of names. The second one checks that the total number of names
...               is three. This should be an unreachable situation, because refinements
...               are always a single scenario and each of the scenarios only inserts a
...               single name. If the rollback of the middle part (2.2 in the trace) was
...               incomplete, i.e. its rollback did not include the refinement scenario
...               as well, then inserting the second low-level scenario would satisfy
...               the first exit conditions and inserting another low-level scenario for
...               the second refinement would satisfy exit conditions for both steps and
...               incorrectly complete the suite.
Suite Setup       Expect failing suite processing
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt


*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

high-level scenario
    Given there is a birthday card
    when The first person writes their name on the birthday card
    and Two more people write their name on the birthday card
    then the birthday card has 3 names written on it

low-level scenario A
    Given there is a birthday card
    and we are in refinement
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it

low-level scenario B
    Given there is a birthday card
    and we are in refinement
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it

low-level scenario C
    Given there is a birthday card
    and we are in refinement
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it


*** Keywords ***
The first person writes their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: scenario.count = len(birthday_card.names)
    ...    :OUT: Someone in birthday_card.names
    Skip when unreachable
    Should Contain    ${names}    Someone

Two more people write their name on the birthday card
    [Documentation]    *model info*
    ...    :IN: scenario.count
    ...    :OUT: len(birthday_card.names) == scenario.count+3
    Skip when unreachable
    Length should be    ${names}    ${2}

we are in refinement
    [Documentation]    Helper to prevent lower-level scenarios from being valid
    ...    at the top-level. (Better for performance)
    ...    *model info*
    ...    :IN: scenario.count
    ...    :OUT: None
    No Operation

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
