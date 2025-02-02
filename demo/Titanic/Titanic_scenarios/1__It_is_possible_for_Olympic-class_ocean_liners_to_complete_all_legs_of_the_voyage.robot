*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Southampton to Cherbourg leg
    Given Titanic is docked in the port of Southampton
    When Titanic departs for the port of Cherbourg
    and Titanic crosses area the English Channel
    and Titanic arrives in the port of Cherbourg
    then Titanic is docked in the port of Cherbourg

Cherbourg to Queenstown leg
    Given Titanic is docked in the port of Cherbourg
    When Titanic departs for the port of Queenstown
    and Titanic crosses area the English Channel
    and Titanic arrives in the port of Queenstown
    then Titanic is docked in the port of Queenstown

Queenstown to New York leg
    Given Titanic is docked in the port of Queenstown
    When Titanic departs for the port of New York
    and Titanic crosses area Atlantic ocean
    and Titanic arrives in the port of New York
    then Titanic is docked in the port of New York
