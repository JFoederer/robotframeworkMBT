*** Settings ***
Library           robotnl
Resource          ../domain_lib/Titanic.resource

*** Keywords ***
Titanic is scheduled for the voyage to New York
    [Documentation]    *model info*
    ...    :IN: new Titanic | Titanic.destination='New York' | Titanic.port=Southampton
    ...         new Voyage | Voyage.date= '1912-04-10' | Voyage.ports_visited= 1
    ...    :OUT: None
    Spawn titanic at location Southampton
    Log    Dear crew, your ship has been assigned to the trip to New York. You are due for departure from the port of Southampton at noon on 1912-04-10.
    Start Journey on 1912-04-10

Titanic is docked in the port of ${port}
    [Documentation]    *model info*
    ...    :MOD: ${port}= [${port}]
    ...    :IN: Titanic.port == ${port}
    ...    :OUT: Titanic.port == ${port} | Voyage.ports_visited+= 1
    Check that    Map area where 'Titanic's position' is located    Equals    ${port}
    Check that    Titanic's speed    equals    0

Titanic sails from ${port A} to ${port B}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == ${port A}
    ...    :OUT: Titanic.port == ${port B}
    Check that    Map area where 'Titanic's position' is located    Equals    ${port B}

Titanic departs for the port of ${port}
    [Documentation]    *model info*
    ...    :IN: Titanic.port is not None
    ...    :OUT: Titanic.port = None
    Point titanic towards location ${port}
    Titanic moves full speed ahead
    Move Titanic out of current area

Titanic arrives in the port of ${port}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None
    ...    :OUT: Titanic.port = ${port} | Titanic.location = 'port'
    Check that    Map area where 'Titanic's position' is located    Equals    ${port}
    Titanic stops

Titanic crosses area ${area}
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None | Titanic.location= 'Iceberg alley' if ${area} == 'Atlantic ocean' else 'port'
    ...    :OUT: Titanic.location != 'Iceberg alley'
    Check that    Map area where 'Titanic's position' is located    Equals    ${area}
    Check that    Titanic's speed    Is Greater Than    0
    Move Titanic out of current area
    Check that    Map area where 'Titanic's position' is located    does not equal    ${area}

Titanic sails the Atlantic
    [Documentation]    *model info*
    ...    :IN: Titanic.port == None
    ...    :OUT: None
    log    Aahh, the fresh air of the open sea!
    Move Titanic out of current area

Titanic crosses Iceberg alley
    [Documentation]    *model info*
    ...    :IN: Titanic.location = 'Iceberg alley'
    ...    :OUT: Titanic.location == 'Atlantic ocean'
    Check that    Map area where 'Titanic's position' is located    Equals    Atlantic ocean

Titanic is sailing Iceberg alley
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: Titanic.location == 'Iceberg alley'
    Move Titanic out of current area
    Check that    Map area where 'Titanic's position' is located    Equals    Iceberg alley
    Log    Brrr, that's a bit chilly

Titanic barely misses a huge iceberg
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: None
    Spawn iceberg at coordinate latitude 47.0000 longitude -48.5000
    Move Titanic out of current area
    Log    Pfew! That was close!

Titanic hits a huge iceberg
    [Documentation]    *model info*
    ...    :IN: Titanic.location == 'Iceberg alley'
    ...    :OUT: None
    Spawn iceberg at coordinate latitude 44.6135 longitude -48.2618
    log    Iceberg, right ahead!
    Move Titanic out of current area

Titanic continues on its voyage
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: Titanic.location = 'Atlantic ocean'
    Check that    Titanic's speed    Is Greater Than    0

Titanic starts to sink
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: Titanic.location = 'Atlantic ocean'
    Check that    Map area where 'Titanic's position' is located    Equals    Iceberg alley
    Check that    Titanic's speed    equals    0

Titanic's voyage is complete
    [Documentation]    *model info*
    ...    :IN: Voyage.date == '1912-04-17'
    ...    :OUT: Voyage.date='1912-04-17' | Titanic.destination=None
    log    Dear passengers, this is the final destination of this journey. Please remember to collect all your personal belongings when disembarking.

the date is ${date}
    [Documentation]    *model info*
    ...    :IN: Voyage.date == ${date}
    ...    :OUT: Voyage.date == ${date}
    Check that    Current date of Journey    equals    ${date}

Titanic sails from ${port A} to ${port B} again
    [Documentation]    *model info*
    ...    :MOD: ${port A}= [port for port in [Southampton, Queenstown, Cherbourg, Plymouth] if port == Titanic.port]
    ...          ${port B}= [port for port in [Southampton, Queenstown, Cherbourg, Plymouth] if port != Titanic.port]
    ...    :IN: Titanic.port == ${port A}
    ...    :OUT: Titanic.port= ${port B}
    Point titanic towards location ${port B}
    Titanic moves full speed ahead
    Move Titanic out of current area
    Move Titanic out of current area
    Check that    Map area where 'Titanic's position' is located    Equals    ${port B}
    Titanic stops

Titanic visited at least ${n} ports
    [Documentation]    *model info*
    ...    :IN: Voyage.ports_visited >= ${n}
    ...    :OUT: Voyage.ports_visited >= ${n}
    log    Wow! Did we already visit ${n} ports!?
