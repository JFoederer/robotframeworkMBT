*** Settings ***
Suite Setup       Treat this test suite Model-based    seed=new
Library           robotmbt
Library           traces.py

*** Test Cases ***
test case 0
    Trace 2 test number 0 is executed

test case 1
    Trace 2 test number 1 is executed

test case 2
    Trace 2 test number 2 is executed

test case 3
    Trace 2 test number 3 is executed

test case 4
    Trace 2 test number 4 is executed

test case 5
    Trace 2 test number 5 is executed

test case 6
    Trace 2 test number 6 is executed

test case 7
    Trace 2 test number 7 is executed

test case 8
    Trace 2 test number 8 is executed

test case 9
    Trace 2 test number 9 is executed
