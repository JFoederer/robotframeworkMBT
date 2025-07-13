*** Settings ***
Documentation     This test suite takes a single basic birthday card scenario, but uses the step
...               definitions previously used as given-when-then steps for action-driven testing
...               instead. Action keywords process their :IN: and : OUT: conditions like when
...               steps. The way this scenario is constructed works because the first keyword
...               has :IN: None, the second was already constructed as a when-step and the last
...               keyword has the same condition for both the :IN: and the : OUT: conditions.
Suite Setup       Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Action-driven scenario omitting given-when-then
    Johan buys a birthday card
    Johan writes their name on the birthday card
    The birthday card has 'Johan' written on it
