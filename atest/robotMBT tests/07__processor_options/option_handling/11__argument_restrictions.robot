*** Settings ***
Library           SuiteRepeater.py
Library           robotmbt    processor_lib=SuiteRepeater    processor=mandatory_repeat_argument

*** Test Cases ***
arguments can be mandatory
    Run keyword and expect error    *SuiteRepeater.mandatory_repeat_argument() missing 1 required keyword-only argument: 'repeat'
    ...    Treat this test suite Model-based    bonus_scenario=${True}

can fail on unknown arguments
    Run keyword and expect error    *SuiteRepeater.mandatory_repeat_argument() got an unexpected keyword argument 'intentional_fail'
    ...    Treat this test suite Model-based    repeat=1    bonus_scenario=${True}    intentional_fail=${True}
