*** Settings ***
Documentation     This suite is a duplicate of the 'Repeating twin with tail' suite, with
...               the addition of an impossible scenario. It turns out that the available
...               combinations in this suite are particularly difficult to handle in case
...               of modelling errors. The purpose of this test is to verify Robotmbt can
...               detect the error and report that no full trace can be constructed.
Suite Setup       Expect failing suite processing
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When 'Johan' buys a birthday card
    then there is a blank birthday card available

Someone writes their name on the card
    Given there is a birthday card
    when 'Someone' writes their name on the birthday card
    then the birthday card has 'Someone' written on it

Someone else writes their name on the card
    Given there is a birthday card
    when 'Someone else' writes their name on the birthday card
    then the birthday card has 'Someone else' written on it

At least 42 people can write their name on the card
    Given the birthday card has 41 names written on it
    when 'Johan' writes their name on the birthday card
    then the birthday card has 42 names written on it

Taking an evelope
    When Johan takes a new envelope
    then there is a blank envelope available

Marking the envelope for the receiver
    Given there is a blank envelope available
    when Johan writes Bahar's name on the evelope
    then the envelope is marked for Bahar

Sealing the card in an evelope
    Given the birthday card has 'Johan' written on it
    and there is an envelope available
    when Johan seals the birthday card inside the envelope
    then the birthday card is no longer accessible

Impossible scenario
    Skip when unreachable
    Given the birthday card has 'XXXX' written on it

*** Keywords ***
Expect failing suite processing
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    [Timeout]    20 seconds
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

Johan takes a new envelope
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new envelope
    Set suite variable    ${envelope_content}    empty
    Set suite variable    ${envelope_face}    blank

there is a blank envelope available
    [Documentation]    *model info*
    ...    :IN: envelope.face == blank
    ...    :OUT: envelope.face = blank
    Should be equal    ${envelope_face}    blank

there is an envelope available
    [Documentation]    *model info*
    ...    :IN: envelope
    ...    :OUT: envelope
    Variable should exist    ${envelope_content}

Johan writes Bahar's name on the evelope
    [Documentation]    *model info*
    ...    :IN: envelope
    ...    :OUT: envelope.face = Bahar
    Set suite variable    ${envelope_face}    Bahar

the envelope is marked for Bahar
    [Documentation]    *model info*
    ...    :IN: envelope.face == Bahar
    ...    :OUT: envelope.face = Bahar
    Should be equal    ${envelope_face}    Bahar

Johan seals the birthday card inside the envelope
    [Documentation]    *model info*
    ...    :IN: envelope
    ...    :OUT: envelope.content = card
    Set suite variable    ${envelope_content}    card

the birthday card is no longer accessible
    [Documentation]    *model info*
    ...    :IN: new birthday_card | del birthday_card
    ...    :OUT: del birthday_card
    ...
    ...    The new/del combo is a trick to check that a domain term is
    ...    not available. There is no direct way to check this yet.
    Log    That's it, no more people can write their name on the card
