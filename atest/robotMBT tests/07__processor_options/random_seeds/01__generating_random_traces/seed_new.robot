*** Settings ***
Suite Setup       Treat this test suite Model-based    seed=new
Library           robotmbt
Library           traces.py

*** Test Cases ***
test case 0
    Trace 'seed=new' test number 0 is executed

test case 1
    Trace 'seed=new' test number 1 is executed

test case 2
    Trace 'seed=new' test number 2 is executed

test case 3
    Trace 'seed=new' test number 3 is executed

test case 4
    Trace 'seed=new' test number 4 is executed

test case 5
    Trace 'seed=new' test number 5 is executed

test case 6
    Trace 'seed=new' test number 6 is executed

test case 7
    Trace 'seed=new' test number 7 is executed

test case 8
    Trace 'seed=new' test number 8 is executed

test case 9
    Trace 'seed=new' test number 9 is executed
