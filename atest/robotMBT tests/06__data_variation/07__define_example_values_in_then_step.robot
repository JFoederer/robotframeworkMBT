*** Settings ***
Documentation     This test suite focuses on the initialisation of model data from a then-step in
...               scenarios with data variation. If certain data from the system under test is
...               predefined externally and you need to get this data into your model, then one
...               simple way of achieving this is to hard code the values into the model info. An
...               alternative way, as demonstrated in this test suite, is to separate the model
...               structure from the model data. The given-step from the background defines the
...               structure of the model data, but leaves some of the values empty. The then-steps
...               are used to fill the model with concrete data. This is useful in the generic
...               sense from the concept of separation of concerns and has pratical applications
...               when there are, for instance, multiple variants of the system under test that
...               are deployed with different settings. The model can then be made to fit the
...               configuration without altering model code.
Suite Setup       Treat this test suite Model-based
Library           robotmbt

*** Test Cases ***
Background
    Given Bahar is throwing a party for their friends
    then Johan is invited to Bahar's party
    and Tannaz is invited to Bahar's party

A friend accepts the invite
    Given Johan is invited to Bahar's party
    when Johan accepts Bahar's party invitation
    then Johan is going to Bahar's party

A second friend accepts the invite
    Given Johan is going to Bahar's party
    and Tannaz is invited to Bahar's party
    when Tannaz accepts Bahar's party invitation
    then 2 persons are going to Bahar's party
    [Teardown]    Frederique did not yet accept Bahar's invite

Making a new friend
    Given 2 persons are going to Bahar's party
    when Bahar becomes friends with Frederique
    then Frederique is invited to Bahar's party
    but Frederique did not yet accept Bahar's invite
    and 2 persons are going to Bahar's party

The new friend joins the party
    Given 2 persons are going to Bahar's party
    when Frederique accepts Bahar's party invitation
    then Frederique is going to Bahar's party
    and 3 persons are going to Bahar's party


*** Keywords ***
${celebrant} is throwing a party for their friends
    [Documentation]    *model info*
    ...    :IN: new party | party.host= ${celebrant}
    ...         party.invitees= [] | party.confirmed_guests= []
    ...    :OUT: False
    @{friends}=    Create list    Johan    Tannaz
    Set suite variable    ${friends}
    @{guest list}=    Create list
    Set suite variable    ${guest list}

${celebrant} becomes friends with ${new friend}
    [Documentation]    *model info*
    ...    :MOD: ${new friend}= [${new friend}]
    ...    :IN: party.host == ${celebrant} | ${new friend} not in party.invitees
    ...    :OUT: None
    @{friends}=    Create list    @{friends}    ${new friend}
    Set suite variable    ${friends}

${invitee} is invited to ${celebrant}'s party
    [Documentation]    *model info*
    ...    :MOD: ${invitee}= party.invitees
    ...    :IN: ${invitee} in party.invitees
    ...    :OUT: party.invitees.append(${invitee})
    Should contain    ${friends}    ${invitee}

${invitee} did not yet accept ${celebrant}'s invite
    [Documentation]    *model info*
    ...    :IN: ${invitee} not in party.confirmed_guests
    ...    :OUT: ${invitee} not in party.confirmed_guests
    Should not contain    ${guest list}    ${invitee}

${invitee} accepts ${celebrant}'s party invitation
    [Documentation]    *model info*
    ...    :MOD: ${invitee}= [f for f in party.invitees if f not in party.confirmed_guests]
    ...    :IN: party.confirmed_guests
    ...    :OUT: party.confirmed_guests.append(${invitee})
    @{guest list}=    Create list     @{guest list}    ${invitee}
    Set suite variable    ${guest list}

${invitee} is going to ${celebrant}'s party
    [Documentation]    *model info*
    ...    :MOD: ${invitee}= party.confirmed_guests
    ...    :IN: ${invitee} in party.confirmed_guests
    ...    :OUT: ${invitee} in party.confirmed_guests
    Should contain    ${guest list}    ${invitee}

${n} persons are going to ${celebrant}'s party
    [Documentation]    *model info*
    ...    :IN: len(party.confirmed_guests) == ${n}
    ...    :OUT: len(party.confirmed_guests) == ${n}
    Length should be    ${guest list}    ${n}
