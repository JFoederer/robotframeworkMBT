*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Southampton to New York
    Given Titanic is docked in the port of Southampton
    When Titanic sails from Southampton to Cherbourg
    and Titanic sails from Cherbourg to Queenstown
    and Titanic sails from Queenstown to New York
    then Titanic is docked in the port of New York
    and Titanic's voyage is complete

Southampton to Cherbourg
    Given Titanic is docked in the port of Southampton
    When Titanic departs for the port of Cherbourg
    and Titanic crosses the English Channel
    and Titanic arrives in the port of Cherbourg
    then Titanic is docked in the port of Cherbourg

Cherbourg to Queenstown
    Given Titanic is docked in the port of Cherbourg
    When Titanic departs for the port of Queenstown
    and Titanic crosses the English Channel
    and Titanic arrives in the port of Queenstown
    then Titanic is docked in the port of Queenstown

Queenstown to New York
    Given Titanic is docked in the port of Queenstown
    When Titanic departs for the port of New York
    and Titanic sails the Atlantic
    and Titanic crosses Iceberg alley
    and Titanic sails the Atlantic
    and Titanic arrives in the port of New York
    then Titanic is docked in the port of New York
