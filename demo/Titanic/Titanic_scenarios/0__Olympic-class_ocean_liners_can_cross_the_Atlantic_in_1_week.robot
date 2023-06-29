*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
The itinerary from Southampton to New York
    Given Titanic is docked in the port of Southampton
    When Titanic sails from Southampton to Cherbourg
    and Titanic sails from Cherbourg to Queenstown
    and Titanic sails from Queenstown to New York
    Then Titanic's voyage is complete

Olympic-class ocean liners can complete the Atlantic crossing from Southampton to New York in 1 week
    Given Titanic is scheduled for the voyage to New York
    and Titanic is docked in the port of Southampton
    and the date is 1912-04-10
    When Titanic sails from Southampton to New York
    then Titanic is docked in the port of New York
    and the date is 1912-04-17

Olympic-class ocean liners can complete the Atlantic crossing from New York to Southampton in 1 week
    Given Titanic is scheduled for the voyage to Southampton
    and Titanic is docked in the port of New York
    and the date is 1912-04-20
    When Titanic sails from New York to Southampton
    then Titanic is docked in the port of Southampton
    and the date is 1912-04-27
