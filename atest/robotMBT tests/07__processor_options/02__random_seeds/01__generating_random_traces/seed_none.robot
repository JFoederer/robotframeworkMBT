*** Settings ***
Suite Setup       Treat this test suite Model-based    seed=${None}
Library           robotmbt
Library           traces.py

*** Test Cases ***
scenario 0
    Trace 'seed=None', scenario number 0 is executed

scenario 1
    Trace 'seed=None', scenario number 1 is executed

scenario 2
    Trace 'seed=None', scenario number 2 is executed

scenario 3
    Trace 'seed=None', scenario number 3 is executed

scenario 4
    Trace 'seed=None', scenario number 4 is executed

scenario 5
    Trace 'seed=None', scenario number 5 is executed

scenario 6
    Trace 'seed=None', scenario number 6 is executed

scenario 7
    Trace 'seed=None', scenario number 7 is executed

scenario 8
    Trace 'seed=None', scenario number 8 is executed

scenario 9
    Trace 'seed=None', scenario number 9 is executed
