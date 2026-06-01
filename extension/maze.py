"""
maze.py.

Create and store the maze structure with horizontal and vertical walls.
"""

__author__ = "Awizha Abroon"
__created__ = "December 5, 2025"


def create_maze(width: int = 5, height: int = 5):
    """
    Create a new maze with the given width and height.

    The maze stores:
        - width and height
        - horizontal inner walls
        - vertical inner walls

    Args:
        width (int): Number of cells horizontally.
        height (int): Number of cells vertically.

    Returns:
        dict: A maze structure.
    """
    maze = {
        "width": width,
        "height": height,
        "horizontal_walls": [],
        "vertical_walls": [],
    }
    return maze


def add_horizontal_wall(maze, x_coordinate: int, horizontal_line: int):
    """
    Add a horizontal wall to the maze.

    Args:
        maze (dict): Maze structure.
        x_coordinate (int): X-location of the wall.
        horizontal_line (int): Y-line of the horizontal wall.

    Returns:
        dict: Updated maze.
    """
    wall = (x_coordinate, horizontal_line)
    maze["horizontal_walls"].append(wall)
    return maze


def add_vertical_wall(maze, y_coordinate: int, vertical_line: int):
    """
    Add a vertical wall to the maze.

    Args:
        maze (dict): Maze structure.
        y_coordinate (int): Y-location of the wall.
        vertical_line (int): X-line of the vertical wall.

    Returns:
        dict: Updated maze.
    """
    wall = (y_coordinate, vertical_line)
    maze["vertical_walls"].append(wall)
    return maze


def get_dimensions(maze):
    """
    Return the width and height of the maze.

    Args:
        maze (dict): Maze structure.

    Returns:
        tuple: (width, height)
    """
    width = maze["width"]
    height = maze["height"]
    return (width, height)


def get_walls(maze, x_coordinate: int, y_coordinate: int):
    """
    Check for walls around a given maze cell.

    A wall exists if:
        - a wall tuple is in the maze, OR
        - the position is at the outer boundary.

    Args:
        maze (dict): Maze structure.
        x_coordinate (int): X-position in the maze.
        y_coordinate (int): Y-position in the maze.

    Returns:
        tuple: (north_wall, east_wall, south_wall, west_wall)
    """
    width = maze["width"]
    height = maze["height"]

    north_wall = (x_coordinate, y_coordinate + 1) in maze[
        "horizontal_walls"
    ] or y_coordinate == height - 1
    east_wall = (y_coordinate, x_coordinate + 1) in maze[
        "vertical_walls"
    ] or x_coordinate == width - 1
    south_wall = (x_coordinate, y_coordinate) in maze[
        "horizontal_walls"
    ] or y_coordinate == 0
    west_wall = (y_coordinate, x_coordinate) in maze[
        "vertical_walls"
    ] or x_coordinate == 0

    return (north_wall, east_wall, south_wall, west_wall)
