*** Settings ***
Suite Setup       Expect failing suite processing
Library           MyProcessor.py
Library           robotmbt    processor_lib=MyProcessor

*** Test Cases ***
fail on empty model info
    Confirm expected error then pass execution    empty model info    When present, *model info* cannot be empty
    empty model info

fail when colon syntax isn't used
    Confirm expected error then pass execution    non-colon model info    *model info* expected format: :<attr>: <expr>|<expr>
    non-colon model info

fail when colon syntax is used incorrectly
    Confirm expected error then pass execution    forgotten opening colon    *model info* expected format: :<attr>: <expr>|<expr>
    forgotten opening colon

fail on non-existing keyword
    Confirm expected error then pass execution    non-existing keyword    No keyword with name 'non-existing keyword' found.
    non-existing keyword

fail on non-existing step with prefix
    Confirm expected error then pass execution    non-existing step    No keyword with name 'when non-existing step' found.
    when non-existing step

*** Keywords ***
Expect failing suite processing
    ${msg}=    Run keyword and expect error    Error(s) detected*    Treat this test suite Model-based
    Set suite variable    ${full_message}    ${msg}

empty model info
    [Documentation]    *model info*
    Fail    Unreachable keyword executed

non-colon model info
    [Documentation]    *model info*
    ...    *IN* Alfa
    ...    *OUT* Beta | Gamma delta | Epsilon
    Fail    Unreachable keyword executed

forgotten opening colon
    [Documentation]    *model info*
    ...    IN: Alfa
    ...    OUT: Beta | Gamma delta | Epsilon
    Fail    Unreachable keyword executed

Confirm expected error then pass execution
    [Arguments]    ${step_name}    ${error_message}
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    ...
    ...    If the scenario is inserted after proper detection of the expected error,
    ...    then this keyword causes the remainder of the scenario to be skipped and
    ...    the test passes. When inserted without the correct error, the scenario
    ...    will fail.
    Should Contain    ${full_message}    ${step_name} FAILED: ${error_message}
    Pass execution    Accepting intentionally unexecutable scenario
