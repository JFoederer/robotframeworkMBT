*** Settings ***
Documentation     This suite uses refinement and equivalence partitioning. The high-level scenario
...               requires just a single key example from the equivalence class and uses just one
...               concrete example. This scenario can be refined by two more detailed examples
...               that use 2 different actors. This implies that one refinement example will match
...               the high-level scenario's example, the other does not. To complete the trace,
...               the high-level scenario must be repeated, once with each possible refinement.
...               The example values between the high- and low-level scenarios must be matched,
...               and kept identical, under refinement.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_data_variation.resource
Library           robotmbt


*** Test Cases ***
Background
    Given Bahar is having their birthday
    and Johan is a friend of Bahar
    and Tannaz is a friend of Bahar
    When Johan buys a birthday card
    then there is a blank birthday card available

A friend signs the birthday card
    Given there is a birthday card
    when Tannaz signs the birthday card
    then the birthday card has a personal touch

Signing the birthday card with your name only
    Given there is a birthday card
    and Johan is signing the birthday card
    when Johan writes their name on the birthday card
    then the birthday card has 'Johan' written on it

Signing the birthday card with a wish
    Given there is a birthday card
    and Tannaz is signing the birthday card
    when Tannaz writes their name on the birthday card
    and Tannaz adds the wish 'Happy birthday!' to the birthday card
    then the birthday card has 'Tannaz' written on it
    and the birthday card proclaims: Happy birthday!
