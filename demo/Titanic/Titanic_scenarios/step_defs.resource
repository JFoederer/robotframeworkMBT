*** Settings ***
Resource          ../domain_lib/Titanic.resource
Library           ../domain_lib/JourneyLib.py
Library           ../domain_lib/TitanicLib.py

*** Keywords ***
Titanic is on its journey
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Spawn titanic at coordinate long 51.12345 lat 23.1122 heading east at speed of 22 knots

Titanic hits a huge iceberg
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Spawn iceberg at coordinate long 51.12345 lat 23.1834
    play out Journey for a duration of 10 minutes

Titanic barely misses a huge iceberg
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Spawn iceberg at coordinate long 51.32345 lat 23.1834
    play out Journey for a duration of 10 minutes

the people are shocked
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    the peaople are shocked

Titanic starts to sinks
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    ${sinking}    Titanic is sinking
    Should Be True    ${sinking}

Titanic continues its journey
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Titanic continues journey
    ${sinking}    Titanic is sinking
    Should Be True    ${sinking} == False

The people are relieved
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    People are relieved
