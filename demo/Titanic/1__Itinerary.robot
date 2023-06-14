*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Southampton to New York
    Given Titanic is docked in Southampton
    When Titanic sails from Southampton to Cherbourg
    and Titanic sails from Cherbourg to Queenstown
    and Titanic sails from Queenstown to New York
    then Titanic's voyage is complete

Southampton to Cherbourg
    Given Titanic is docked in Southampton
    When Titanic departs from port Southampton
    and Titanic crosses the Channel
    and Titanic arrives in Cherbourg
    then Titanic is docked in Cherbourg

Cherbourg to Queenstown
    Given Titanic is docked in Cherbourg
    When Titanic departs from port Cherbourg
    and Titanic crosses the Channel
    and Titanic arrives in Queenstown
    then Titanic is docked in Queenstown

Queenstown to New York
    Given Titanic is docked in Queenstown
    When Titanic departs from port Queenstown
    and Titanic sails the Atlantic
    and Titanic crosses Iceberg alley
    and Titanic sails the Atlantic
    and Titanic arrives in New York
    then Titanic is docked in New York
