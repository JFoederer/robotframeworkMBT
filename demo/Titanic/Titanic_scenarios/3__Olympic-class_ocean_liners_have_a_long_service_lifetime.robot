*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Titanic sails back to Europe
    [Tags]    extended
    Given Titanic is docked in the port of New York
    When Titanic departs for the port of Plymouth
    and Titanic crosses area Atlantic ocean
    and Titanic arrives in the port of Plymouth

    When Titanic departs for the port of Cherbourg
    and Titanic crosses area the English Channel
    and Titanic arrives in the port of Cherbourg
    then Titanic is docked in the port of Cherbourg

Titanic takes a different route
    [Tags]    extended
    Given Titanic visited at least 8 ports
    when Titanic sails from its current port to a previous location again
    then Titanic is docked in the port of a previous location

Titanic docks in Europe for its first large maintenance
    [Tags]    extended
    Given Titanic visited at least 30 ports
    when Titanic sails from Queenstown to Southampton again
    then Titanic is docked in the port of Southampton
