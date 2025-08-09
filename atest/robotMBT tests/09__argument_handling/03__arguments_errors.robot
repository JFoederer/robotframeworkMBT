*** Settings ***
Documentation     This test suite shows that faulty argument usage is reoprted. I.e. when the
...               provided arguments do not match the keyword's signature.
Suite Setup       Expect failing suite processing
Library           robotmbt

*** Test Cases ***
Too many arguments provided
    Confirm expected error then pass execution    Keyword without arguments    Keyword 'Keyword without arguments' expected 0 arguments, got 1.
    Keyword without arguments    A

Not enough arguments provided
    Confirm expected error then pass execution    Keyword with positional argument    Keyword 'Keyword with positional argument' expected 1 argument, got 0.
    Keyword with positional argument

Unknown argument provided
    Confirm expected error then pass execution    Keyword with positional argument    Non-existing named argument 'fake'.
    Keyword with positional argument    fake=pos1

*** Keywords ***
Expect failing suite processing
    ${msg}=    Run keyword and expect error    Steps with errors in their model*    Treat this test suite Model-based
    Set suite variable    ${full_message}    ${msg}

Keyword without arguments
    Fail    Unreachable keyword executed

Keyword with positional argument
    [Arguments]    ${pos1}
    Fail    Unreachable keyword executed

Confirm expected error then pass execution
    [Arguments]    ${step_name}    ${error_message}
    [Documentation]
    ...    If the scenario is inserted after proper detection of the expected error,
    ...    then this keyword causes the remainder of the scenario to be skipped and
    ...    the test passes. When inserted without the correct error, the scenario
    ...    will fail.
    Should Contain    ${full_message}    ${step_name} [${error_message}]
    Pass execution    Accepting intentionally unexecutable scenario
