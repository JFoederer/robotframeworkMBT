*** Settings ***
Suite Setup       Run keyword and expect error    *    Treat this test suite Model-based
Library           MyProcessor.py
Library           robotmbt    processor_lib=MyProcessor

*** Test Cases ***
fail on empty model info
    empty model info

fail when colon syntax isn't used
    non-colon model info

fail when colon syntax is used incorrectly
    forgotten opening colon

*** Keywords ***
empty model info
    [Documentation]    *model info*
    @{errors}=    Reported errors
    Should be equal    ${errors[0].bare_kw}    empty model info

non-colon model info
    [Documentation]    *model info*
    ...    *IN* Alfa
    ...    *OUT* Beta | Gamma delta | Epsilon
    @{errors}=    Reported errors
    Should be equal    ${errors[1].bare_kw}    non-colon model info

forgotten opening colon
    [Documentation]    *model info*
    ...    IN: Alfa
    ...    OUT: Beta | Gamma delta | Epsilon
    @{errors}=    Reported errors
    Should be equal    ${errors[2].bare_kw}    forgotten opening colon
