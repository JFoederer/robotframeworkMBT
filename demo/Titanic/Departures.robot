*** Test Cases ***
Getting everything on board for departure
  Given the ship is docked in the harbour, preparing for the departure
  when the ship is fueled up
  and the supplies are stocked
  and the cargo is loaded
  and the passengers are on board
  and the crew is on board
  then the ship is ready for departure

Preparation for departure took longer than planned
  Given the ship is ready for departure
  when the planned departure time is passed
  then the ship departs

The journey starts when the ship leaves the harbour
  Given the ship departs
  when the ship leaves the harbour
  then the ship is on its journey
  and the current time is the departure time for the itenerary's section
