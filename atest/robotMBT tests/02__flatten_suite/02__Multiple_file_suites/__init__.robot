*** Settings ***
Documentation     Each setup, test case and teardown increases the keyword counter. Checks are done within specific steps to see that they are executed following the correct sequence.
Suite Setup       Suite setup
Suite Teardown    Should be equal    ${kw_count}    ${20}
Library           robotmbt    processor=flatten
Resource          setup_teardown_keywords.resource

*** Keywords ***
Suite setup
    Set Global Variable    ${kw_count}    ${0}
    Treat this test suite Model-based
