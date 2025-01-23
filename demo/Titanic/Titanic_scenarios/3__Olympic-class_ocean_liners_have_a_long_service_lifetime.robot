*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Titanic sails back to Europe
    Given Titanic is docked in the port of New York
    When Titanic departs for the port of Queenstown
    and Titanic sails the Atlantic
    and Titanic crosses Iceberg alley
    and Titanic sails the Atlantic
    and Titanic arrives in the port of Queenstown
    then Titanic is docked in the port of Queenstown

Titanic roams the seas
    when Titanic sails from Cherbourg to Southampton again
    then Titanic is docked in the port of Southampton

Titanic can reach New York at least 4 times
    Given Titanic visited New York 3 times
    when Titanic sails from Queenstown to New York
    then Titanic visited New York 4 times
