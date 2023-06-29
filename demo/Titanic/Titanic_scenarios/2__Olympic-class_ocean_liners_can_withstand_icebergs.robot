*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Titanic hits a huge iceberg and continues on its voyage
    Given Titanic is sailing Iceberg alley
    when Titanic hits a huge iceberg
    then Titanic continues on its voyage

Titanic barely misses an iceberg and continues on its voyage
    Given Titanic is sailing Iceberg alley
    when Titanic barely misses a huge iceberg
    then Titanic continues on its voyage
