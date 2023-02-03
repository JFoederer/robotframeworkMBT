*** Settings ***
Resource          ../domain_lib/Titanic.resource

*** Test Cases ***
Titanic hits iceberg
    Given Titanic is on its journey
    when Titanic hits a huge iceberg
    then the people are shocked
    and Titanic starts to sinks

Titanic misses the iceberg
    Given Titanic is on its journey
    when Titanic barely misses a huge iceberg
    then Titanic continues its journey
    and The people are relieved
