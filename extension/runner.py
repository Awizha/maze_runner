"""
runner.py.

Control runner movement and maze exploration using the left-hand rule.
It uses a left-hand rule to follow the walls and find its way by
checking where the walls are.
"""

__author__ = "Awizha Abroon"
__created__ = "December 5, 2025"

from typing import Optional, Tuple, List

from maze import get_walls, get_dimensions


def create_runner(x: int = 0, y: int = 0, orientation: str = "N"):
    """
    Create and return a runner represented as a dictionary.

    Default starting position is (0, 0) facing North.

    Args:
        x (int): Initial x-coordinate.
        y (int): Initial y-coordinate.
        orientation (str): One of "N", "E", "S", or "W".

    Returns:
        dict: Runner state with keys 'x', 'y', and 'orientation'.
    """
    return {"x": x, "y": y, "orientation": orientation}


def get_x(runner):
    """Return the x-coordinate of the runner."""
    return runner["x"]


def get_y(runner):
    """Return the y-coordinate of the runner."""
    return runner["y"]


def get_orientation(runner):
    """Return the facing direction of the runner."""
    return runner["orientation"]


def turn(runner, direction: str):
    """
    Turn the runner left or right.

    Args:
        runner (dict): Runner state.
        direction (str): "Left" or "Right".

    Returns:
        dict: A new runner dict with updated orientation.
    """
    left_turn = {"N": "W", "W": "S", "S": "E", "E": "N"}
    right_turn = {"N": "E", "E": "S", "S": "W", "W": "N"}

    current = runner["orientation"]

    if direction == "Left":
        new_orientation = left_turn[current]
    elif direction == "Right":
        new_orientation = right_turn[current]
    else:
        raise ValueError("Direction must be 'Left' or 'Right'.")

    return {
        "x": runner["x"],
        "y": runner["y"],
        "orientation": new_orientation,
    }


def forward(runner):
    """
    Move the runner forward by 1 cell based on its current orientation.

    Returns:
        dict: Updated runner state.
    """
    x = runner["x"]
    y = runner["y"]
    orientation = runner["orientation"]

    if orientation == "N":
        y += 1
    elif orientation == "S":
        y -= 1
    elif orientation == "E":
        x += 1
    elif orientation == "W":
        x -= 1

    return {"x": x, "y": y, "orientation": orientation}


def sense_walls(runner, maze):
    """
    Sense walls relative to the runner's current orientation.

    Returns:
        tuple: (left_wall, front_wall, right_wall)
    """
    x = get_x(runner)
    y = get_y(runner)
    orientation = get_orientation(runner)
    north, east, south, west = get_walls(maze, x, y)

    if orientation == "N":
        left_wall = west
        front_wall = north
        right_wall = east
    elif orientation == "E":
        left_wall = north
        front_wall = east
        right_wall = south
    elif orientation == "S":
        left_wall = east
        front_wall = south
        right_wall = west
    elif orientation == "W":
        left_wall = south
        front_wall = west
        right_wall = north
    else:
        raise ValueError("Invalid orientation.")

    return (left_wall, front_wall, right_wall)


def go_straight(runner, maze):
    """
    Move forward if the front cell is not blocked.

    Returns:
        dict: Updated runner state.
    """
    left, front, right = sense_walls(runner, maze)
    if front:
        raise ValueError("Wall in front. Cannot move ahead")

    return forward(runner)


def turn_left(runner):
    """Turn the runner left."""
    return turn(runner, "Left")


def turn_right(runner):
    """Turn the runner right."""
    return turn(runner, "Right")


def turn_back(runner):
    """Turn the runner 180 degrees."""
    return turn_left(turn_left(runner))


def move(runner, maze):
    """
    Perform a left-hand wall-following move.

    Returns:
        tuple: (new_runner, action_string)
    """
    left_wall, front_wall, right_wall = sense_walls(runner, maze)

    if not left_wall:
        new_runner = turn_left(runner)
        new_runner = go_straight(new_runner, maze)
        return new_runner, "LF"

    elif not front_wall:
        new_runner = go_straight(runner, maze)
        return new_runner, "F"

    elif not right_wall:
        new_runner = turn_right(runner)
        new_runner = go_straight(new_runner, maze)
        return new_runner, "RF"

    new_runner = turn_back(runner)
    new_runner = go_straight(new_runner, maze)
    return new_runner, "B"


def explore(
    runner, maze, goal: Optional[Tuple[int, int]] = None
) -> List[Tuple[int, int, str]]:
    """
    Explore the maze until the goal cell is reached.

    Args:
        runner (dict): Runner state.
        maze (dict): Maze structure.
        goal (tuple, optional): Target (x, y) cell. Default is bottom-right.

    Returns:
        list: A list of (x, y, action) tuples for each move taken.
    """
    if goal is None:
        max_x, max_y = get_dimensions(maze)
        goal = (max_x - 1, max_y - 1)

    path = []

    while (get_x(runner), get_y(runner)) != goal:
        current_x = get_x(runner)
        current_y = get_y(runner)

        runner, action = move(runner, maze)
        path.append((current_x, current_y, action))

    return path
