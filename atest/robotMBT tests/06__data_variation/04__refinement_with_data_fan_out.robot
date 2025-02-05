*** Settings ***
Documentation     This suite uses refinement and equivalence partitioning. The high-level scenario
...               requires just a single key example from the equivalence class and uses just one
...               concrete example. This scenario is then refined by two more detailed examples
...               that use 2 different actors with specific characters. One is concise, the other
...               a bit more elaborate. This implies that for at least one set of examples the
...               high-level scenario's example value does not match the low-level scenario's
...               example value. They must however still be matched, and kept identical, under
...               refinement.
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
