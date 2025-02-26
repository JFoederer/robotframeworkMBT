*** Settings ***
Documentation     This suite focuses on data variation based on equivalence partitioning. An action
...               step, or when-step, often uses data from just a single equivalence class. In that
...               case, the when-step's modifier can directly specify its data. This allows an
...               example value to be used for the first time in a scenario in the when-step. This
...               is demonstrated in the example using _when ${person} writes..._. Other situations
...               require a when-step (_when ${person} tries to write..._) to deal with multiple
...               independent equivalence classes (celebrants or friends). To ensure that the
...               when-step uses a value from the correct equivalence class, it must rely on prior
...               constraints.
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

A friend addresses the birthday card to the celebrant
    Given there is a birthday card
    and Bahar is the birthday celebrant
    when Johan writes their name on the birthday card
    and Johan writes Bahar's address on the birthday card
    then Bahar's address is on the birthday card

Friends prevent each other from making mistakes
    Given there is a birthday card
    and Bahar is the birthday celebrant
    and Frederique is a friend of Bahar
    when Johan writes their name on the birthday card
    and Johan tries to write Frederique's address on the birthday card
    then Frederique alerts Johan that it is Bahar's birthday

A friend checks the address while writing
    Given there is a birthday card
    and Bahar is the birthday celebrant
    when Johan writes their name on the birthday card
    and Johan tries to write Bahar's address on the birthday card
    and Tannaz confirms Bahar's address
    then Bahar's address is on the birthday card
