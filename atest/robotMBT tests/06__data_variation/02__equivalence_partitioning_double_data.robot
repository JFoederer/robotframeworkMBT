*** Settings ***
Documentation     This suite focuses on data variation based on equivalence partitioning and
...               additionally makes use of the same equivalence class twice in the same scenario.
...               Because the example is about two distinct values, the model must also choose
...               different values for the two arguments. Note: In opposition to regular use, the
...               examples that need to be combined use contradicting examples. This is to force
...               this suite to fail when data variation is not applied at all.
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

The first friend writes their name on the card
    Given there is a birthday card
    and Tannaz's name is not yet on the birthday card
    and Frederique's name is not yet on the birthday card
    when Tannaz writes their name on the birthday card
    then the birthday card has 'Tannaz' written on it
    but Frederique's name is not yet on the birthday card

A second friend writes their name on the card
    Given there is a birthday card
    and the birthday card has 'Johan' written on it
    but Tannaz's name is not yet on the birthday card
    when Tannaz writes their name on the birthday card
    then the birthday card has 'Johan' written on it
    and the birthday card has 'Tannaz' written on it
    and the birthday card has 2 different names written on it
