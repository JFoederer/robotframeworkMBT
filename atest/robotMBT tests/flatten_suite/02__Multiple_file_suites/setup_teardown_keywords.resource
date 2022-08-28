*** Keywords ***
Test 1.1 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${2}

Test 1.2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${3}

Test 1.2 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${5}

Test 1.3 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${6}

Test 2.1 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${9}

Test 2.2 setup
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${13}

Test 2.2 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${15}

Test 2.3 teardown
    Set Global Variable    ${kw_count}    ${kw_count+1}
    Should be equal    ${kw_count}    ${19}
