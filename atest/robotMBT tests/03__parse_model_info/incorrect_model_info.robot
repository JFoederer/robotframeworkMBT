*** Settings ***
Suite Setup       Expect failing suite processing
Library           MyProcessor.py
Library           robotmbt    processor_lib=MyProcessor

*** Test Cases ***
fail on empty model info
    empty model info

fail when colon syntax isn't used
    non-colon model info

fail when colon syntax is used incorrectly
    forgotten opening colon

fail on non-existing keyword
    Confirm expected error then pass execution    3    No keyword with name 'non-existing keyword' found.
    non-existing keyword

fail on non-existing step with prefix
    Confirm expected error then pass execution    4    No keyword with name 'when non-existing step' found.
    when non-existing step

*** Keywords ***
Expect failing suite processing
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Run keyword and expect error    Error(s) detected*    Treat this test suite Model-based
    Set suite variable    ${expected_error_detected}    ${True}

empty model info
    [Documentation]    *model info*
    @{errors}=    Reported errors
    Should be equal    ${errors[0].kw_wo_gherkin}    empty model info

non-colon model info
    [Documentation]    *model info*
    ...    *IN* Alfa
    ...    *OUT* Beta | Gamma delta | Epsilon
    @{errors}=    Reported errors
    Should be equal    ${errors[1].kw_wo_gherkin}    non-colon model info

forgotten opening colon
    [Documentation]    *model info*
    ...    IN: Alfa
    ...    OUT: Beta | Gamma delta | Epsilon
    @{errors}=    Reported errors
    Should be equal    ${errors[2].kw_wo_gherkin}    forgotten opening colon

Confirm expected error then pass execution
    [Arguments]    ${index}    ${error_message}
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    ...
    ...    If the scenario is inserted after proper detection of the expected error,
    ...    then this keyword causes the remainder of the scenario to be skipped and
    ...    the test passes. When inserted without the correct error, the scenario
    ...    will fail.
    @{errors}=    Reported errors
    Should be equal    ${errors[${index}].model_info['error']}    ${error_message}
    IF    ${expected_error_detected}
        Pass execution    Accepting intentionally unexecutable scenario
    END
