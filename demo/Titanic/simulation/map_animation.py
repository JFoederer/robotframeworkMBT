import math

from simulation.iceberg import Iceberg
from simulation.titanic_in_ocean import TitanicInOcean


class MapAnimation:
    def __init__(self):
        self.fig = self.ax = None
        self.plot_initialized = False

    def _import_dependencies(self):
        global plt, Rectangle
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

    def plot_static_elements(self, areas, locations):
        # Plot the areas as squares
        if not self.plot_initialized:
            self._import_dependencies()  # Import here, to avoid any missing dependency problems in case matplotlib is not installed

            self.fig, self.ax = plt.subplots()
            self.ax.set_aspect('equal')

        for area_name, area in areas.items():
            width = abs(area.upper_left_bound.latitude - area.lower_right_bound.latitude)
            height = abs(area.upper_left_bound.longitude - area.lower_right_bound.longitude)
            rect = Rectangle((area.lower_right_bound.longitude, area.upper_left_bound.latitude),
                             height, width, alpha=0.4)
            self.ax.add_patch(rect)
            self.ax.annotate(area_name, (area.lower_right_bound.longitude,
                             area.upper_left_bound.latitude), color='black')

        # Plot the locations
        colors = [
            'ro',
            'bo',
            'go',
            'mo',
            'r*',
            'b*',
            'g*',
            'm*',
        ]
        ci = 0
        for location_name, location in locations.items():
            self.ax.plot(location.longitude, location.latitude, colors[ci % len(colors)], label=location_name)
            ci += 1

        # # Set the Atlantic area bounds atlantic_area = MapLib.atlantic_area width = abs(
        # atlantic_area.upper_left_bound.longitude - atlantic_area.lower_right_bound.longitude) height = abs(
        # atlantic_area.upper_left_bound.latitude - atlantic_area.lower_right_bound.latitude) rect = Rectangle((
        # atlantic_area.lower_right_bound.latitude, atlantic_area.upper_left_bound.longitude), height, width,
        # linestyle='--', edgecolor='g', facecolor='none') self.ax.add_patch(rect) self.ax.annotate('Atlantic Area',
        # (atlantic_area.lower_right_bound.latitude, atlantic_area.upper_left_bound.longitude), color='g')

        # Set the plot title and labels
        self.ax.set_title('Current Situation')
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')

        # Add a legend
        self.ax.legend()

        # Show the plot
        if not self.plot_initialized:
            plt.ion()
            plt.show(block=False)
            self.plot_initialized = True
        else:
            plt.draw()
            plt.pause(0.001)

    def update_floating_objects(self, floating_objects):
        if not self.plot_initialized:
            return

        # Clear the floating objects plot
        for artist in self.ax.lines:
            if isinstance(artist.get_gid(), str) and 'floating_object' in artist.get_gid():
                artist.remove()
        # Clear the floating objects plot
        for artist in self.ax.texts:
            if isinstance(artist.get_gid(), str) and 'floating_object' in artist.get_gid():
                artist.remove()

        # Plot the floating objects
        for obj in floating_objects:
            if isinstance(obj, TitanicInOcean):  # Set the rotation angle in degrees
                angle_degrees = obj.direction

                # Convert angle to radians
                angle_radians = math.radians(angle_degrees)
                aspect_ratio = self.ax.get_data_ratio()

                # Compute the arrow components
                dx = math.sin(angle_radians)
                dy = math.cos(angle_radians)

                # Draw the arrow
                self.ax.annotate("", xy=(obj.longitude + dx, obj.latitude + dy), xytext=(obj.longitude, obj.latitude),
                                 arrowprops=dict(arrowstyle="->"), gid='floating_object')

                if obj.sunk:
                    icon = 'rs'  # red square
                else:
                    icon = 'ys'  # yellow square
                    # Draw the arrow
                    self.ax.annotate("", xy=(obj.longitude + dx, obj.latitude + dy), xytext=(obj.longitude, obj.latitude),
                                     arrowprops=dict(arrowstyle='->'), gid='floating_object')
                self.ax.plot(obj.longitude, obj.latitude, icon, label='Titanic', gid='floating_object')
            elif isinstance(obj, Iceberg):
                self.ax.plot(obj.longitude, obj.latitude, 'w^', label='Iceberg', gid='floating_object')

        # Redraw the plot
        plt.draw()
        plt.pause(0.001)


# Create the MapAnimation instance
map_animation = MapAnimation()
