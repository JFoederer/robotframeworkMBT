*** Settings ***
Documentation     To prove that model info is processed for action keywords, two scenarios are
...               needed. Scenario 1, Omitting given-when-then, shows that action keywords are
...               accepted. This would however also be the case if the model info were not
...               processed at all. To complete the check the scenario should fail when the first
...               step of buying the birthday card is omitted. Together with the previous scenario
...               this proves that :IN: conditions are processed, following the expected failure
...               of this scenario, but also that :OUT: conditions are processed, following the
...               passing of the previous scenario.
Suite Setup       Run keyword and expect error    Unable to compose a consistent suite    Treat this test suite Model-based
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
Action keyword cannot start due to precondition mismatch
    Pass execution    Accepting intentionally unexecutable scenario
    Johan writes their name on the birthday card
    The birthday card has 'Johan' written on it
