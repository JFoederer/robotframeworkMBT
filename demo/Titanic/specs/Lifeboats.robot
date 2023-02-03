*** Settings ***
Resource        ../domain_lib/Titanic_the_ship.resource

*** Settings ***
Documentation   As a passenger or crew member
...             I want to have a seat available on a lifeboat
...             so that I can evacuate in case of emergency

*** Test Cases ***
Lifeboats for maiden voyage
  Given there are 2224 people on board
  when the ship is on its journey
  then there are at least 2224 seats available in the lifeboats
