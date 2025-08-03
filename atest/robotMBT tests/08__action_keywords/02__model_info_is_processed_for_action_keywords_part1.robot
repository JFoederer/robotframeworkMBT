*** Settings ***
Documentation     To prove that model info is processed for action keywords, two scenarios are
...               needed. This first scenario shows that, if the :IN: condition of a keyword
...               depends on certain model info that is not available, the trace generation will
...               fail. The scenario in the next suite shows that the condition can be satisified
...               by inserting a keyword that sets the condition.
Suite Setup       Run keyword and expect error    Unable to compose a consistent suite    Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Action keyword cannot start due to precondition mismatch
    Pass execution    Accepting intentionally unexecutable scenario
    Write name 'Johan' on the birthday card
