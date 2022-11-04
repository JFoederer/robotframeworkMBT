*** Settings ***
Documentation     This is a composed scenario where there is a sequence of three
...               scenarios on the highest level. The middle of these three scenarios
...               has multiple steps that require refinement. One of those refinement
...               steps needs refinement of it own, yielding double-layerd refinement.
Suite Setup       Treat this test suite Model-based
Resource          birthday_cards_composed.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    When buying a birthday card
    then there is a blank birthday card

Sending Bahar a birthday card
    Given there is a blank birthday card
    when 'Johan' writes their name on the birthday card
    and 'Johan' writes Bahar's address on the birthday card
    and 'Tannaz' writes their name on the birthday card
    and 'Nicolas' writes their name on the birthday card
    then 'Johan' puts the birthday card in the mail

Bahar receives the birthday card
    Given a birthday card for Bahar was put in the mail
    when the birthcard is is delivered to Bahar's mailbox
    then 'Bahar' received the birthday card

Johan prefers pen
    Given 'Johan' writes their name on the birthday card
    then 'Johan' writes their name in pen on the birthday card

Tannaz prefers traditional style
    Given 'Tannaz' writes their name on the birthday card
    when 'Tannaz' writes their first letter as a piece of art
    and 'Tannaz' writes the other letters in decorative writing
    then 'Tannaz' is written as calligraphy on the birthday card

Nicolas prefers pencil
    Given 'Nicolas' writes their name on the birthday card
    when there is a pencil available
    then 'Nicolas' writes their name in pencil on the birthday card

Nicolas' pencil needs sharpening
    Given 'Nicolas' writes their name in pencil on the birthday card
    but the pencil has a broken tip
    when the tip of the pencil is sharpend
    then 'Nicolas' writes their name in pencil on the birthday card
