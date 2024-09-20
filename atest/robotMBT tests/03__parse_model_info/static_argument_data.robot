*** Settings ***
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
leading scenario
    When 'Johan' buys a birthday card
    then there is a blank birthday card available

Simple argument
    Given there is a birthday card
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it

Argument data is case sensitive
    Given there is a birthday card
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it
    but the birthday card does not have 'JOHAN' written on it

Argument with spaces
    Given there is a birthday card
    when 'Gert Jan' writes their name on the birthday card
    then the birthday card has 'Gert Jan' written on it
