*** Settings ***
Documentation     When using multiple given, when or then steps, you can choose to connect them
...               using the 'and' or 'but' composite prefixes. Processing of the model info depends
...               on which kind of step keyword it is. When using the composite prefixes, the
...               interpretation depends on the previous step. Action keywords are not really
...               expected to be mixed in with the given-when-then style, but you wouldn't want
...               your scenario to break the instant you add e.g. some debugging keywords.
...               Therefore, action keywords are not considered when deciding the step type for
...               keywords that start with a composite prefix.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
leading scenario
    When Johan buys a birthday card
    then there is a blank birthday card available

Interrupted givens
    Given there is a blank birthday card available
    Log    Given-block interrupted by action keyword, 'and' treated as Given
    and fail if :OUT: is processed

Interrupted whens
    when Johan writes their name on the birthday card
    Log    When-block interrupted by action keyword, 'and' treated as When
    and fail if :OUT: is processed without :IN:

Interrupted thens
    then the birthday card has 'Johan' written on it
    Log    Then-block interrupted by action keyword, 'and' treated as Then
    and fail if :IN: is processed

Double interrupt
    then the birthday card has 'Johan' written on it
    Log    Then-block interrupted by action keyword, 'and' treated as Then
    Log    Second interruption
    and fail if :IN: is processed

Interrupt followed by but-step
    then the birthday card has 'Johan' written on it
    Log    Then-block interrupted by action keyword, 'but' treated as Then
    but fail if :IN: is processed


*** Keywords ***
fail if :OUT: is processed
    [Documentation]    *model info*
    ...    :IN:  new tracker
    ...    :OUT: False
        Length should be    ${names}    0

fail if :OUT: is processed without :IN:
    [Documentation]    *model info*
    ...    :IN:  tracker.in_condition = True
    ...    :OUT: tracker.in_condition == True
        Length should be    ${names}    1

fail if :IN: is processed
    [Documentation]    *model info*
    ...    :IN:  False
    ...    :OUT: tracker.in_condition == True
        Length should be    ${names}    1
