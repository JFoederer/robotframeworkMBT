*** Settings ***
Suite Setup       Treat this test suite Model-based
Library           MyProcessor.py
Library           robotmbt    processor_lib=MyProcessor

*** Test cases ***
consise model info
    consise model info

trailing model info
    trailing model info

leading model info
    leading model info

sandwitched model info
    sandwitched model info

model info on multiple lines
    model info on multiple lines

model info with altenative spacing
    model info with altenative spacing

*** Keywords ***
consise model info
    [Documentation]    *model info*
    ...    :IN: Alfa
    ...    :OUT: Beta | Gamma delta | Epsilon
    Log    Hello world!

trailing model info
    [Documentation]    Text
    ...    before model info
    ...    *model info*
    ...    :IN: Alfa
    ...    :OUT: Beta | Gamma delta | Epsilon
    Log    Hello world!

leading model info
    [Documentation]    *model info*
    ...    :IN: Alfa
    ...    :OUT: Beta | Gamma delta | Epsilon
    ...
    ...    text after model info
    Log    Hello world!

sandwitched model info
    [Documentation]    Text
    ...    before model info
    ...
    ...    *model info*
    ...    :IN: Alfa
    ...    :OUT: Beta | Gamma delta | Epsilon
    ...
    ...    text after model info
    Log    Hello world!

model info on multiple lines
    [Documentation]    Text
    ...    *model info*
    ...    :IN: Alfa
    ...    :OUT: Beta
    ...    Gamma delta |
    ...    | Epsilon |
    Log    Hello world!

model info with altenative spacing
    [Documentation]    Text
    ...    before model info
    ...
    ...    *model info*
    ...    :IN : Alfa
    ...    : OUT: Beta |Gamma delta|
    ...    |Epsilon |
    ...
    ...    text after model info
    Log    Hello world!
