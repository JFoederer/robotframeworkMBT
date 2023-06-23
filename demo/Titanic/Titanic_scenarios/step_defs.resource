*** Settings ***
Library           robotnl
Library           ../domain_lib/JourneyLib.py
Library           ../domain_lib/TitanicLib.py

*** Keywords ***
Titanic is scheduled for the voyage to New York
    [Documentation]    *model info*
    ...    :IN: new Titanic | Titanic.destination='New York' | Titanic.port=Southampton
    ...    new Date | Date.now='10 April 1912'
    ...    :OUT: None
    set suite variable    ${systems check}    All good!
    Log    Dear crew, your ship has been assigned to the cross-atlantic. You are due for departure from Southampton port at noon on 10 April 1912.

Titanic is docked in ${port}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == '${port}'
    ...    :OUT: Titanic.port == '${port}'
    log    Anchored safely in the port of ${port}
    Check that    'Titanic's Location' is within the Map area of ${port}

the date is ${date}
    [Documentation]    *model info*
    ...    :IN: Date.now == '${date}'
    ...    :OUT: Date.now == '${date}'
    log    The calendar shows that today is ${date}

Titanic sails from ${port A} to ${port B}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == '${port A}'
    ...    :OUT: Titanic.port == '${port B}'
    Should be equal    ${systems check}    All good!
    log    Completed the leg from ${port A} to ${port B}

Titanic's voyage is complete
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: Date.now='17 April 1912' | Titanic.destination=None
    Should be equal    ${systems check}    All good!
    log    Dear passengers, this is the final port on this journey. Please remember to collect all your personal belongings when disembarking.

Titanic departs from port ${port}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == '${port}'
    ...    :OUT: Titanic.port = None
    log    Good bye, people of ${port}!
    Point titanic towards location ${port}
    Titanic moves full speed ahead
    Move Titanic out of current area

Titanic arrives in ${port}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None
    ...    :OUT: Titanic.port = '${port}'
    log    Nice to meet you, people of ${port}.
    Check that    'Titanic's Location' is within the Map area of ${port}
    Titanic stops

Titanic crosses ${area}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None
    ...    :OUT: None
    log    A short trip within Europe
    Check that    'Titanic's Location' is within the Map area of ${area}
    Check that    Titanic's speed    Is Greater Than    0
    Move Titanic out of current area

Titanic sails the Atlantic
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None
    ...    :OUT: None
    Should be equal    ${systems check}    All good!
    log    Aahh, the fresh air of the open sea!

Titanic is sailing Iceberg alley
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: Titanic.location == 'Iceberg alley'
    log    Iceberg, right ahead!

Titanic barely misses a huge iceberg
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: None
    log    Pfew! That was close!

Titanic continues on its voyage
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: Titanic.location = 'Atlantic ocean'
    log    That was quite an adventure!

Titanic hits a huge iceberg
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: None
    set suite variable    ${systems check}    Whoopsy
    log    Oh darn :-o

Titanic starts to sinks
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: Titanic.location = 'Atlantic ocean'
    log    Blub blub blub

Titanic crosses Iceberg alley
    [Documentation]    *model info*
    ...    :IN: Titanic.location = 'Iceberg alley'
    ...    :OUT: Titanic.location == 'Atlantic ocean'
    Log    Brrr, that's a bit chilly
    Should be equal    ${systems check}    All good!
