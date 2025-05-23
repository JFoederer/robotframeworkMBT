*** Settings ***
Suite Setup       Treat this test suite Model-based    seed=${None}
Library           robotmbt
Library           traces.py

*** Test Cases ***
test case 0
    Trace 'seed=None' test number 0 is executed

test case 1
    Trace 'seed=None' test number 1 is executed

test case 2
    Trace 'seed=None' test number 2 is executed

test case 3
    Trace 'seed=None' test number 3 is executed

test case 4
    Trace 'seed=None' test number 4 is executed

test case 5
    Trace 'seed=None' test number 5 is executed

test case 6
    Trace 'seed=None' test number 6 is executed

test case 7
    Trace 'seed=None' test number 7 is executed

test case 8
    Trace 'seed=None' test number 8 is executed

test case 9
    Trace 'seed=None' test number 9 is executed
