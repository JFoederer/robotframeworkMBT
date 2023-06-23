*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Complete cross-Atlantic service within 1 week
    Given Titanic is scheduled for the voyage to New York
    and Titanic is docked in the port of Southampton
    and the date is 10 April 1912
    When Titanic sails from Southampton to New York
    then the date is 17 April 1912
