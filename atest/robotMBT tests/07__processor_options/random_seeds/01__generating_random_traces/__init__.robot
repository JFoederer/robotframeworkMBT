*** Settings ***
Documentation     In this suite a set of sub-suites are executed using trace generation. Their
...               trace generation should be independent and each yield a random trace. This is
...               verified by checking that all traces are unique. The traces consist of 10
...               indepent scenarios, giving over 3.500.000 options. This makes the  risk of
...               hitting the same trace by chance acceptable.
Suite Setup       Reset traces
Suite Teardown    All traces should be different
Library           robotmbt
Library           traces.py

*** Keywords ***
All traces should be different
    @{traces}=    Get all traces
    FOR    ${trace}    IN    @{traces}
        ${count}=    Get count    ${traces}    ${trace}
        Should be equal    ${count}    ${1}
    END
