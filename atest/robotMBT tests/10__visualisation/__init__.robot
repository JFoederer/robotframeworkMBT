*** Settings ***
Suite Setup       Skip if optional visualisation is not installed
Library           graph_checker.py

*** Keywords ***
Skip if optional visualisation is not installed
    ${partial_installation}=    Graphing dependencies missing
    Skip If    ${partial_installation}    Visualisation dependencies not installed. Please read the README for information on how to do this.
