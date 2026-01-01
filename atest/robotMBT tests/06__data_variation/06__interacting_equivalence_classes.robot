*** Settings ***
Documentation     This suite focuses on data variation based on equivalence partitioning. It uses
...               two different equivalence classes in the same scenario that interact with each
...               other. In one of the two cases the example values are identical. We must assume
...               that the author chose to use the same example value for a purpose, therefore the
...               model must also keep the values identical under data variation. The other case
...               takes the opposite situation. The author chose two different example values,
...               therefore the model must also ensure two different values are selected. Note: In
...               opposition to regular use, the background contradicts the examples. This is to
...               force this suite to fail when data variation is not applied at all.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_data_variation.resource
Library           robotmbt


*** Test Cases ***
Background
    Given Johan is having their birthday
    and Bahar is a friend of Johan
    and Johan is a friend of Johan
    When Johan buys a birthday card
    then there is a blank birthday card available

A namesake of the birthday celebrant writes their name and the address
    Given there is a birthday card
    and Bahar is the birthday celebrant
    when Bahar writes their name on the birthday card
    and Bahar writes Bahar's address on the birthday card
    then the birthday card has 'Bahar' written on it
    and the birthday celebrant's name, Bahar, is written on the card
    and Bahar's address is on the birthday card

Another friend writes their name on the card
    Given there is a birthday card
    and Bahar is the birthday celebrant
    when Johan writes their name on the birthday card
    then the birthday card has 'Johan' written on it
    and the birthday celebrant's name, Bahar, is not written on the card
