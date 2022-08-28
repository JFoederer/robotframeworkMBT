*** Settings ***
Library           DateTime

*** Keywords ***
The ship is docked in the harbour, preparing for the departure
    Set Suite Variable    ${current_ship}    Titanic
    Log    Engines are off
    Log    Ropes are tied
    Log    Walking boards are extended
    Log    Cargo cranes are deployed
    Log    Captain on the bridge

Model the ship is docked in the harbour, preparing for the departure
    Set Model preconditions    None
    Set Model postconditions    new ship    ship.name\=Titanic    ship.state\=preparing_for_departure    ship.people_on_board\=0    ship.lifeboat_seats\=1178

the ship is ready for departure
    Log    waiting for further instructions

Model the ship is ready for departure
    Set Model preconditions    ship.state\=\=preparing_for_departure or ship.state\=\=ready_for_departure
    Set Model postconditions    ship.state\=ready_for_departure

The ship is fueled up
    Log    Cleaning out the old ash
    Log    Loading 8000 ton coal in ${current_ship}'s bunker
    Log    Refitting filters for water pumps

Model the ship is fueled up
    Set Model preconditions    None
    Set Model postconditions    None

the supplies are stocked
    Log    Loading beverages
    Log    Loading snacks
    Log    Loading something healthy

Model the supplies are stocked
    Set Model preconditions    None
    Set Model postconditions    None

the cargo is loaded
    Log    Loading mail for Royal mail
    Log    Loading painting La Circassienne au Bain for Mauritz Håkan Björnström-Steffansson

Model the cargo is loaded
    Set Model preconditions    None
    Set Model postconditions    None

the passengers are on board
    Log    Embarking third class
    Log    Embarking second class
    Log    Waiting for first class passengers
    Log    Embarking first class

Model the passengers are on board
    Set Model preconditions    ship.people_on_board
    Set Model postconditions    ship.people_on_board+\=1316

the crew is on board
    Log    Captain Edward John Smith
    Log    Chief mate Henry Tingle Wilde
    Log    Lookout Fredrick Fleet
    Log    Lookout Reginald Lee
    Log    And 904 others

Model the crew is on board
    Set Model preconditions    ship.people_on_board
    Set Model postconditions    ship.people_on_board+\=908

the planned departure time is passed
    Log    Well, we are just over 100 years late, so I guess the time has passed

Model the planned departure time is passed
    Set Model preconditions    None
    Set Model postconditions    None

the ship departs
    Log    Starting the engines
    Log    Untying the ropes
    Log    Navigating through the harbour

Model the ship departs
    Set Model preconditions    ship.state\=\=ready_for_departure or ship.state\=\=departing
    Set Model postconditions    ship.state\=departing

the ship leaves the harbour
    Log    Arriving in open water

model the ship leaves the harbour
    Set Model preconditions    ship.state\=\=departing
    Set Model postconditions    ship.state\=journey

the ship is on its journey
    Log    Sailing the sea

model the ship is on its journey
    Set Model preconditions    ship.state\=\=journey
    Set Model postconditions    None

the current time is the departure time for the itenerary's section
    ${now}=    Get current date
    Log    Captain's log: Official registered time of departure ${now}

model the current time is the departure time for the itenerary's section
    Set Model preconditions    None
    Set Model postconditions    None

there are ${n} people on board
    Log    Counting crew: 908
    Log    Counting passengers: 1316
    Log    Not counting the rats

model there are ${n} people on board
    Set Model preconditions    ship.people_on_board\=\=${n}
    Set Model postconditions    None

Available lifeboats
    Log    14 standard wooden lifeboats x65 seats: capacity 910 people
    Log    4 collapsible lifeboats x47 seats: capacity 188 people
    Log    2 emergency cutters x40 seats: capacity 80 people
    Log    grand total: 1178 seats available
    [Return]    ${1178}

there are at least ${n} seats available in the lifeboats
    ${lifeboat_seats}=    Available lifeboats
    Should Be True    ${lifeboat_seats} >= ${n}

model there are at least ${n} seats available in the lifeboats
    Set Model preconditions    ship.lifeboat_seats
    Set Model postconditions    None
