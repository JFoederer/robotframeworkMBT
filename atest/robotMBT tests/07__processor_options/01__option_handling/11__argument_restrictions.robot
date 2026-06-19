*** Settings ***
Library           strictsuiterepeater.py
Library           robotmbt    processor=strictsuiterepeater

*** Test Cases ***
arguments can be mandatory
    Run keyword and expect error    *StrictSuiteRepeater.process_test_suite() missing 1 required keyword-only argument: 'repeat'
    ...    Treat this test suite Model-based    bonus_scenario=${True}

can fail on unknown arguments
    Run keyword and expect error    *StrictSuiteRepeater.process_test_suite() got an unexpected keyword argument 'intentional_fail'
    ...    Treat this test suite Model-based    repeat=1    bonus_scenario=${True}    intentional_fail=${True}
