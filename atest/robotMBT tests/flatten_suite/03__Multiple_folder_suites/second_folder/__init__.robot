*** Settings ***
Suite Setup       Set Global Variable    ${kw_count}    ${kw_count+1}
Suite Teardown    Set Global Variable    ${kw_count}    ${kw_count+1}
Test Setup        Set Global Variable    ${kw_count}    ${kw_count+1}
Test Teardown     Set Global Variable    ${kw_count}    ${kw_count+1}
