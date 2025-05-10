*** Settings ***
Documentation     In this suite two sets of scenarios are executed using trace generation. Their
...               trace generation should be independent and yield unique traces. Both traces
...               consist of 10 indepent scenario, giving a chance less than 1 in 3.500.000 of
...               hitting the same trace by chance.
Suite Setup       init trace variables
Suite Teardown    final check on traces
Library           robotmbt
Library           traces.py

*** Keywords ***
final check on traces
    ${trace1}=    get trace    1
    ${trace2}=    get trace    2
    Should not be equal    ${trace1}    ${trace2}
