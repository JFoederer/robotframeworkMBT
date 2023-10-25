from time import sleep

from simulation.iceberg import Iceberg
from simulation.journey import Journey
from simulation.location_on_grid import LocationOnGrid, AreaOnGrid
from simulation.map_animation import map_animation
from simulation.ocean import Ocean
import simulation.ocean
from simulation.titanic_in_ocean import TitanicInOcean
from system.titanic import Titanic

locations = {
    'Southampton': LocationOnGrid(50.909698, -1.404351),
    'Cherbourg': LocationOnGrid(49.630001, -1.620000),
    'Queenstown': LocationOnGrid(51.850334, -8.294286),
    'New York': LocationOnGrid(40.730610, -73.935242)
}

areas = {
    'The English Channel': AreaOnGrid(LocationOnGrid(49.5, -1.41), LocationOnGrid(51.9, -8.2)),
    'Iceberg alley': AreaOnGrid(LocationOnGrid(43, -45), LocationOnGrid(48, -50))
}

atlantic_area = AreaOnGrid(LocationOnGrid(35, -1.41), LocationOnGrid(65, -74))

def run_game(map_animation, journey, tio: TitanicInOcean, atlantic_area):

    import curses

    # Increase threshold such that it is easier to hit the iceberg in the game.
    simulation.ocean.COLLISION_THRESHOLD = 1

    def main_game_loop(stdscr):
        # Set up the window
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(100)  # Refresh every 100 milliseconds
        stdscr.addstr(0, 0, "Q=Quit. 0=Stop Titanic. WASD-controls (WS control speed, AD control rotation, no need to press and hold)")

        while True:
            journey.passed_time(100)

            map_animation.update_floating_objects(journey.ocean.floating_objects)

            if not atlantic_area.is_location_within_area(tio):
                tio.direction -= 180
                journey.passed_time(100)
                tio.speed = 0

            if tio.distance_to(locations['New York']) < 0.4:
                tio.speed = 0
                stdscr.addstr(1, 0, "You made it to NY!!")

            if tio.sunk:
                stdscr.addstr(1, 0,
                              "You SUNK!!! Press Q to exit.")

            # Get user input
            key = stdscr.getch()

            # Handle different key presses
            if key == ord('q') or key == ord('Q'):  # QUIT
                break  # Exit the game loop

            if not tio.sunk:
                if key == ord('a') or key == ord('A'):
                    tio.direction -= 10

                if key == ord('d') or key == ord('D'):
                    tio.direction += 10

                if key == ord('w') or key == ord('W'):
                    tio.speed += 10

                if key == ord('s') or key == ord('S'):
                    tio.speed -= 10

            if key == ord('0'):
                tio.speed = 0

            # Continue with the rest of the game logic


    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()  # Disable automatic echoing of pressed keys
    curses.cbreak()  # React to keys instantly without requiring Enter

    # Run the game
    curses.wrapper(main_game_loop)

    # Clean up curses
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == '__main__':

    LOCATION_AREA_THRESHOLD = 0.1
    ATLANTIC_AREA = 'Atlantic'

    ocean = Ocean()

    draw_areas = areas.copy()
    draw_areas['Atlantic Ocean'] = atlantic_area
    map_animation.plot_static_elements(draw_areas, locations)

    location = locations["Southampton"]

    t = Titanic(0, steering_direction=0)
    tio = TitanicInOcean(t, location.longitude, location.latitude - 0.1, 0, 0)
    ocean.floating_objects.append(tio)

    iceberg = Iceberg(45, -47.5)
    ocean.floating_objects.append(iceberg)

    journey = Journey(ocean)

    map_animation.update_floating_objects(ocean.floating_objects)

    run_game(map_animation, journey, tio, atlantic_area)

