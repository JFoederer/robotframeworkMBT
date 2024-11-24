*** Settings ***
Documentation     This suite focuses on data variation based on equivalence partitioning and
...               additionally uses refinement. The high-level scenario uses data from an
...               equivalence class, the same selected data must be used at the lower-level.
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
    when a friend signs the birthday card
    then the birthday card has a personal touch

Signing a birthday card
    Given there is a birthday card
    when the friend writes their name on the birthday card
    and the friend adds the wish 'Happy birthday!' to the birthday card
    then the birthday card has 'the friend's name' written on it
    and the birthday card proclaims: Happy birthday!
