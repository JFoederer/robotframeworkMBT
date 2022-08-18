*** Settings ***
Suite Setup       Treat this test suite Model-based
Resource          birthday_cards.resource
Library           robotmbt

*** Test Cases ***
leading scenario
    Given a blank birthday card
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it

trailing scenario
    Given the birthday card has 'Johan' written on it
    when 'Tannaz' writes their name on the birthday card
    then the birthday card has 'Johan' written on it
    and the birthday card has 'Tannaz' written on it
