*** Settings ***
Documentation     This suite focuses on data variation based on equivalence partitioning.
...               Even though no specific value is mentioned in the scenario, the model
...               must make the sceanrio concrete by picking a value. The final scenario
...               can only be completed if different values are chosen from the same
...               equivalence class.
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

A friend writes their name on the card
    Given there is a birthday card
    and a friend's name is not yet on the birthday card
    when the friend writes their name on the birthday card
    then the birthday card has 'the friend's name' written on it

At least 3 people can write their name on the card
    Given the birthday card has 2 different names written on it
    and a friend's name is not yet on the birthday card
    when the friend writes their name on the birthday card
    then the birthday card has 3 different names written on it
