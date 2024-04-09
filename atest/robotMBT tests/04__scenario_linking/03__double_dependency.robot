*** Settings ***
Documentation     There are three test cases, one must go first. The other two are both
...               valid as a second scenario. However, if you pick the wrong one, the
...               third scenario cannot be added anymore, because its precondition will
...               fail. The scenarios are included in the suite in reverse order to
...               force the model to reorganise the scenarios.
Suite Setup       Suite setup
Suite Teardown    Should be equal    ${test_count}    ${3}
Test Setup        Test setup
Resource          ../../resources/birthday_cards_flat.resource
Library           robotmbt

*** Test Cases ***
trailing scenario
    Given there is a birthday card
    when 'Tannaz' writes their name on the birthday card
    then the birthday card has 'Tannaz' written on it
    [Teardown]    Check order    ${3}

middle scenario
    Given there is a blank birthday card available
    when 'Johan' writes their name on the birthday card
    then the birthday card has 'Johan' written on it
    and the birthday card has 1 name written on it
    [Teardown]    Check order    ${2}

leading scenario
    When 'Johan' buys a birthday card
    then there is a blank birthday card available
    [Teardown]    Check order    ${1}

*** Keywords ***
Suite setup
    Set Global Variable    ${test_count}    ${0}
    Treat this test suite Model-based

Test setup
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Set Global Variable    ${test_count}    ${test_count+1}

Check order
    [Arguments]    ${order}
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Should be equal    ${test_count}    ${order}
