*** Settings ***
Documentation     This suite is an extension to the 'data fan out' suite, which needed refinement
...               for just a single step. Here, the high-level scenario needs refinement in three
...               of its steps. The background defines three actors and there are three refinement
...               scenarios available. One for each actor. However, the high-level scenario only
...               uses two of the actors, forcing the model to match up two of the steps and to
...               never use the third option. The test fails if the model does not properly keep
...               its data choices over all its steps when splitting the high-level scenario, and
...               picks data independently in each step.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_data_variation.resource
Library           robotmbt


*** Test Cases ***
Background
    Given Bahar is having their birthday
    and Johan is a friend of Bahar
    and Tannaz is a friend of Bahar
    and Frederique is a friend of Bahar
    When Johan buys a birthday card
    then there is a blank birthday card available

A friend signs the birthday card
    Given there is a birthday card
    when Johan signs the birthday card
    and Tannaz signs the birthday card
    and Johan signs the birthday card again
    then the birthday card has a personal touch
    and the birthday card has 2 different names written on it

Signing the birthday card with your name only
    Given there is a birthday card
    and Johan is signing the birthday card
    when Johan writes their name on the birthday card
    then the birthday card has 'Johan' written on it

Signing the birthday card with: Happy birthday!
    Given there is a birthday card
    and Tannaz is signing the birthday card
    when Tannaz writes their name on the birthday card
    and Tannaz adds the wish 'Happy birthday!' to the birthday card
    then the birthday card has 'Tannaz' written on it
    and the birthday card proclaims: Happy birthday!

Signing the birthday card with: Cheers!
    Given there is a birthday card
    and Frederique is signing the birthday card
    when Frederique writes their name on the birthday card
    and Frederique adds the wish 'Cheers!' to the birthday card
    then the birthday card has 'Frederique' written on it
    and the birthday card proclaims: Cheers!


*** Keywords ***
${person} signs the birthday card again
    [Documentation]    Similar to '${person} signs the birthday card', but
    ...    without the check that the name is not already on there.
    ...
    ...    *model info*
    ...    :MOD: ${person}= [guest for guest in party.guests]
    ...    :IN: scenario.guest = ${person} | scenario.count = len(birthday_card.names)
    ...    :OUT: len(birthday_card.names) == scenario.count+1
    Should contain    ${names}    ${person}
