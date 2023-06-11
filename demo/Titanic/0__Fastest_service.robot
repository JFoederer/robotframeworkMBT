*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Complete_cross_Atlantic_service_within_1_week
    Given Titanic is scheduled for the voyage to New York
    and Titanic is docked in Southampton
    and the date is 10 April 1912
    When Titanic sails to New York
    then the date is 17 April 1912
