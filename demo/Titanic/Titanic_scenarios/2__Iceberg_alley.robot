*** Settings ***
Resource          step_defs.resource

*** Test Cases ***
Titanic barely misses an iceberg
    Given Titanic is sailing Iceberg alley
    when Titanic barely misses a huge iceberg
    then Titanic continues on its voyage

Titanic hits a huge iceberg
    Given Titanic is sailing Iceberg alley
    when Titanic hits a huge iceberg
    then Titanic starts to sink
