*** Settings ***
Documentation     Has a suite teardown and pushes test teardown to all tests.
...               The tests do not have teardowns.
...               Accounts for a total of 4 tests and 5 teardowns.
Suite Teardown    Set Global Variable    ${teardown_count}    ${teardown_count+1}
Test Teardown     Set Global Variable    ${teardown_count}    ${teardown_count+1}
