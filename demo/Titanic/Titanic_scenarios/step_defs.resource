*** Settings ***
Resource          ../domain_lib/Titanic.resource
Library           ../domain_lib/JourneyLib.py

*** Keywords ***
Titanic is on its journey
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Spawn titanic at coordinate N41 W39 with a heading of 270 and at speed of 22 knots

Titanic hits a huge iceberg
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Spawn iceberg at coordinate N41 W38
    Pass time

the people are shocked
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    the peaople are shocked

Titanic starts to sinks
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Titanic starts to sink

Titanic barely misses a huge iceberg
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Titanic barely misses a huge iceberg

Titanic continues its journey
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Titanic continues journey

The people are relieved
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    People are relieved
