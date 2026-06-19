*** Settings ***
Documentation     Due to refinement, the high-level scenario is split up to insert the low-level
...               scenario. Coverage is not completed until the final part of the split-up
...               scenario is executed.
Suite Setup       Treat this test suite Model-based    coverage_target=1
Suite Teardown    Final checks
Test Teardown     Set suite variable    ${scenario_count}    ${scenario_count+1}
Resource          ../../../resources/birthday_cards_composed.resource
Library           robotmbt


*** variables ***
${scenario_count}          ${0}
${high_level_started}      ${0}
${high_level_completed}    ${0}


*** Test Cases ***
Buying a card
    When someone buys a birthday card
    then there is a blank birthday card available

high-level scenario
    Set suite variable    ${high_level_started}    ${high_level_started+1}
    Given there is a birthday card
    when Someone writes their name on the birthday card
    then the birthday card has 'Someone' written on it
    Set suite variable    ${high_level_completed}    ${high_level_completed+1}

low-level scenario
    Given there is a birthday card
    when Someone writes their name in pen on the birthday card
    then the birthday card has 'Someone' written on it
    and there is text added in ink on the birthday card


*** Keywords ***
Final checks
    Should be equal    ${scenario_count}          ${3}
    Should be equal    ${high_level_started}      ${1}
    Should be equal    ${high_level_completed}    ${1}
