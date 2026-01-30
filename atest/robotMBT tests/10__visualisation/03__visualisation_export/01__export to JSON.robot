*** Settings ***
Documentation     Export and import a test suite from and to JSON
...               and check that the imported suite equals the 
...               exported suite.
Suite Setup       Enter test suite
Resource          ../../../resources/visualisation.resource
Library           robotmbt

*** Keywords ***
Enter test suite
    Check requirements
    Treat this test suite Model-based

*** Test Cases ***
Setup
  Given test suite s has trace info t
  When the algorithm inserts 'A1' with state "attr: states = ['a1'], special='!'"
  And the algorithm inserts 'A2' with state "attr: states = ['a1', 'a2'], special='!'"
  Then test suite s has 2 steps in its current trace 

Backtrack and Insert
  Given test suite s has 2 steps in its current trace  
  When the algorithm backtracks by 1 step(s)
  And the algorithm inserts 'B1' with state "attr: states=['a1', 'b1'], special='!'"    
  Then test suite s has 2 total traces
  And test suite s has 2 steps in its current trace 

Export test suite to json file
  Given test suite s has 2 total traces
  When test suite s is exported to json
  Then the file s.json exists

Load json file into robotmbt 
  Given the file s.json exists
  When s.sjon is imported
  Then trace info from s.json is the same as trace info t

Clean-up
  Given the file s.json exists
  And s.json has been imported
  When s.sjon is deleted
  Then s.json does not exist