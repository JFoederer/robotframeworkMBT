*** Settings ***
Documentation     This suite includes multiplicity on multiple ends. Most notable are:
...               - Two scenarios that are equaly valid to include in the repetition part
...               - Two scenarios at the tail end that cannot be reached without the
...               \ \ repetitions, but each has a different style entry condition.
Suite Setup       Treat this test suite Model-based  graph=scenario
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When Johan buys a birthday card
    then there is a blank birthday card available

Someone writes their name on the card
    Given there is a birthday card
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it

Someone else writes their name on the card
    Given there is a birthday card
    when Someone else writes their name on the birthday card
    then the birthday card has 'Someone else' written on it

At least 42 people can write their name on the card
    Given the birthday card has 41 names written on it
    when Johan writes their name on the birthday card
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

*** Keywords ***
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
