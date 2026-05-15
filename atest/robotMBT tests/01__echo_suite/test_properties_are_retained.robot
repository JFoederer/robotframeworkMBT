*** Settings ***
Documentation     When reconstructing test cases it is expected that attributes belonging to the
...               test case will remain untouched.
Suite Setup       Treat this test suite Model-based
Test Tags         my suite tag
Library           robotmbt    processor=echo

*** Test Cases ***
Tags are retained
    [Tags]    my tag
    Should Contain    ${TEST TAGS}    my tag
    Should Contain    ${TEST TAGS}    my suite tag

Documentation is retained
    [Documentation]    my documentation
    Should Be Equal    ${TEST DOCUMENTATION}    my documentation
