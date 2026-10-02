*** Settings ***
Documentation     This test suite focuses on modifier expressions that have variable assignments.
...               These assignments should be executed in the order they are encountered:
...               steps from top to bottom within a scenario, :MOD: statements from top to bottom within a step,
...               assignments from left to right within a :MOD: statement.
Suite Setup       Treat this test suite Model-based
Library           robotmbt


*** Test Cases ***
Background
    [Tags]     debug
    Given Bahar is throwing a party for their friends
    then Johan is invited to Bahar's party
    and Tannaz is invited to Bahar's party
    and Johan knows Jan
    and Johan knows Pieter
    and Tannaz knows Petra
    and Tannaz knows Arend

A friend accepts the invite
    [Tags]     debug
    Given Johan is invited to Bahar's party
    when Johan accepts Bahar's party invitation
    then Johan is going to Bahar's party

A guest comes along
    [Tags]     debug
    Given Johan is going to Bahar's party
    and Johan knows Jan
    then Bahar becomes friends with Jan
    and Jan is invited to Bahar's party



*** Keywords ***
${celebrant} is throwing a party for their friends
    [Documentation]    *model info*
    ...    :IN: new party | party.host= ${celebrant} | new friends | friends.map = {}
    ...         party.invitees= [] | party.confirmed_guests= []
    ...    :OUT: False
    @{friends}=    Create list    Johan    Tannaz
    Set suite variable    ${friends}
    @{guest list}=    Create list
    Set suite variable    ${guest list}


${guest} knows ${friend}
    [Documentation]    *model info*
    ...    :MOD: scenario.testvar = "Johan" | ${guest} = [scenario.testvar] | ${friend} = friends.map[scenario.testvar]
    ...    :IN: ${friend} in friends.map[${guest}]
    ...    :OUT: friends.map[${guest}].append(${friend})
    No Operation

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
    ...    :OUT: party.invitees.append(${invitee}) | friends.map[${invitee}] = []
    Should contain    ${friends}    ${invitee}

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
