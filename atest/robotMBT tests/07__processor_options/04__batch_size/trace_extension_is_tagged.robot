*** Settings ***
Documentation     This test suite checks that Batch size for trace generation is respected and that
...               the (logging for) trace generation can be found, even when it is not part of the
...               initial 'Treat this test suite model-based' keyword. To find the delayed parts of
...               trace generation, the scenarios that trigger trace extension are tagged. Since
...               tagging is not done until `end_test`, a listener is used to check and confirm
...               that the expected scenarios are tagged.
...
...               Note that tagging is not the preferred solution, but alternatives failed due to
...               Robot Framework's scoping limitations.
Suite Setup       Treat this test suite Model-based    batch_size=2
Suite Teardown    Should Be Equal    ${confirmed_passes}    ${3}
Test Tags         my tag
Library           robotmbt
Library           tag_listener.py


*** Variables ***
${confirmed_passes}    ${0}


*** Test Cases ***
Scenario 1
    No Operation

Scenario 2
    No Operation

Scenario 3
    No Operation
