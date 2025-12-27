*** Settings ***
Documentation     Export and import a test suite from and to JSON
...               and check that the imported suite equals the 
...               exported suite.
Suite Setup       Treat this test suite Model-based     graph=scenario
Resource          ../../resources/visualisation.resource
Library           robotmbt

*** Test Cases ***
Create test suite
    Given test suite s
    Then test suite s has trace info t
    and trace info t has current trace c 
    and current trace c has a tuple 'scenario i, state p: v=1'
    and current trace c has a tuple 'scenario j, state p: v=2'
    and trace info t has all traces a
    and all traces a has list l
    and list l has a tuple 'scenario i, state p: v=2'

Export test suite to json file
    Given test suite s contains trace info t
    When test suite s is exported to json
    Then the file s.json exists

Load json file into robotmbt 
    Given the file s.json exists
    When s.json is imported
    Then trace info from s.json is the same as trace info t
    and flag cleanup is set

Cleanup
    Given the file s.json exists
    and flag cleanup has been set
    When s.json is deleted
    Then s.json does not exist