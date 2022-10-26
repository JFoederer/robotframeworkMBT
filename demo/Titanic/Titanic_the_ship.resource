*** Settings ***
Library           DateTime

*** Keywords ***
The ship is docked in the harbour, preparing for the departure
    [Documentation]    *model info*
    ...    :IN: new ship | ship.name=Titanic
    ...         ship.state=preparing_for_departure | ship.people_on_board=0
    ...    :OUT: None
    Set Suite Variable    ${current_ship}    Titanic
    Log    Engines are off
    Log    Ropes are tied
    Log    Walking boards are extended
    Log    Cargo cranes are deployed
    Log    Captain on the bridge

the ship is ready for departure
    [Documentation]    *model info*
    ...    :IN: ship.state==ready_for_departure
    ...    :OUT: ship.state=ready_for_departure
    Log    waiting for further instructions

The ship is fueled up
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Cleaning out the old ash
    Log    Loading 8000 ton coal in ${current_ship}'s bunker
    Log    Refitting filters for water pumps

the supplies are stocked
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Loading beverages
    Log    Loading snacks
    Log    Loading something healthy

the cargo is loaded
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Loading mail for Royal mail
    Log    Loading painting La Circassienne au Bain for Mauritz Håkan Björnström-Steffansson

the passengers are on board
    [Documentation]    *model info*
    ...    :IN: ship.people_on_board
    ...    :OUT: ship.people_on_board+=1316
    Log    Embarking third class
    Log    Embarking second class
    Log    Waiting for first class passengers
    Log    Embarking first class

the crew is on board
    [Documentation]    *model info*
    ...    :IN: ship.people_on_board
    ...    :OUT: ship.people_on_board+=908
    Log    Captain Edward John Smith
    Log    Chief mate Henry Tingle Wilde
    Log    Lookout Fredrick Fleet
    Log    Lookout Reginald Lee
    Log    And 904 others

the planned departure time is passed
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Log    Well, we are just over 100 years late, so I guess the time has passed

the ship departs
    [Documentation]    *model info*
    ...    :IN: ship.state==departing
    ...    :OUT: ship.state=departing
    Log    Starting the engines
    Log    Untying the ropes
    Log    Navigating through the harbour

the ship leaves the harbour
    [Documentation]    *model info*
    ...    :IN: ship.state==departing
    ...    :OUT: ship.state=journey
    Log    Arriving in open water

the ship is on its journey
    [Documentation]    *model info*
    ...    :IN: ship.state==journey
    ...    :OUT: None
    Log    Sailing the sea

the current time is the departure time for the itenerary's section
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    ${now}=    Get current date
    Log    Captain's log: Official registered time of departure ${now}

there are ${n} people on board
    [Documentation]    *model info*
    ...    :IN: ship.people_on_board==${n}
    ...    :OUT: ship.people_on_board=${n}
    Log    Counting crew: 908
    Log    Counting passengers: 1316
    Log    Not counting the rats

Available lifeboats
    Log    14 standard wooden lifeboats x65 seats: capacity 910 people
    Log    4 collapsible lifeboats x47 seats: capacity 188 people
    Log    2 emergency cutters x40 seats: capacity 80 people
    Log    grand total: 1178 seats available
    [Return]    ${1178}

there are at least ${n} seats available in the lifeboats
    [Documentation]    *model info*
    ...    :IN: ship.lifeboat_seats >= ${n}
    ...    :OUT: ship.lifeboat_seats=${n}
    ${lifeboat_seats}=    Available lifeboats
    Should Be True    ${lifeboat_seats} >= ${n}
