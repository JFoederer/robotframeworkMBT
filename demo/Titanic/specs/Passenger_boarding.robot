*** Settings ***
Resource          ../domain_lib/Titanic_the_ship.resource

*** Test cases ***
Boarding all passengers
    Given no passengers have boarded yet
    when boarding third class passengers
    when boarding second class passengers
    when boarding first class passengers
    then all passengers are on board
