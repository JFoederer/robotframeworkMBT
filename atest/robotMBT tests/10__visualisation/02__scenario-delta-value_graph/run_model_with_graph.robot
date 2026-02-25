*** Settings ***
Documentation     This suite runs model-based with the graphing option enabled. The checks for the contents
...               of the graph are delegated to the second robot file in the same folder. Export/import
...               functionality is used to gain access to the graph contents.
Suite Setup       Treat this test suite Model-based    graph=scenario-delta-value    export_graph_data=${OUTPUT_DIR}
Resource          ../../../resources/birthday_cards_data_variation.resource
Library           robotmbt

*** Test Cases ***
Buying a card
    Given Jonathan is having their birthday
    and Douwe is a friend of Jonathan
    and Diogo is a friend of Jonathan
    and Tycho is a friend of Jonathan
    and Thomas is a friend of Jonathan
    When Douwe buys a birthday card
    then there is a blank birthday card available

Someone writes their name on the card
    Given there is a birthday card
    and Diogo's name is not yet on the birthday card
    when Diogo writes their name on the birthday card
    then the birthday card has 'Diogo' written on it

At least 3 people can write their name on the card
    Given the birthday card has 2 different names written on it
    and Tycho's name is not yet on the birthday card
    when Tycho writes their name on the birthday card
    then the birthday card has 3 different names written on it
