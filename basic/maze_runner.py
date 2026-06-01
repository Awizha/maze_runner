"""
maze_runner.py.

Read maze files and find shortest paths using runner exploration.

This file is part of the Maze Runner coursework. It reads a maze file,
checks the starting and goal positions, finds the shortest path using the
runner exploring algorithm, and outputs exploration data, statistics, and
results.

It can be run from the command line using:

    python3 maze_runner.py <maze_file> --starting x,y --goal x,y

"""

__author__ = "Awizha Abroon"
__created__ = "December 5, 2025"

import argparse
import csv
import maze
import runner


def maze_reader(maze_file: str):
    """
    Read and parse a text file into a maze object.

    Walls are represented by '#' and passages by '.'.

    Args:
        maze_file (str): Path to the maze text file.

    Returns:
        dict: A maze object.
    """
    # Read all lines from the file
    try:
        with open(maze_file, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]
    except OSError:
        raise IOError("Could not read maze file.")

    # Check if file is empty
    if len(lines) == 0:
        raise ValueError("Maze file is empty.")

    # Check all lines have the same lenght
    row_len = len(lines[0])
    for line in lines:
        if len(line) != row_len:
            raise ValueError("Maze lines have inconsistent lengths.")
    # Check for valid chars "#" and "."
    for line in lines:
        for char in line:
            if char not in ("#", "."):
                raise ValueError("Maze contains invalid characters.")

    # Calculate maze dimensions (must be odd)
    total_rows = len(lines)
    total_cols = row_len

    if total_rows % 2 == 0 or total_cols % 2 == 0:
        raise ValueError("Maze dimensions must be odd.")

    height = (total_rows - 1) // 2
    width = (total_cols - 1) // 2

    # create maze structure
    maze_obj = maze.create_maze(width, height)

    # Horizontal walls
    for row_idx in range(0, total_rows, 2):
        y = (total_rows - 1 - row_idx) // 2
        line = lines[row_idx]
        for x in range(width):
            idx = 2 * x + 1
            if line[idx] == "#":
                maze.add_horizontal_wall(maze_obj, x, y)

    # Vertical walls
    for row_idx in range(1, total_rows, 2):
        y = (total_rows - 1 - row_idx) // 2
        line = lines[row_idx]
        for v_line in range(width + 1):
            idx = 2 * v_line
            if line[idx] == "#":
                maze.add_vertical_wall(maze_obj, y, v_line)

    return maze_obj


def _parse_position(pos_str):
    """
    Parse a position string into an (x, y) tuple.

    Args:
        pos_str (str | None): Position string in "x,y" format.

    Returns:
        tuple | None: Parsed (x, y) or None.
    """
    if pos_str is None:
        return None

    coord_parts = pos_str.split(",")
    if len(coord_parts) != 2:
        raise ValueError("Use 'x,y' format.")

    # convert to int
    x = int(coord_parts[0].strip())
    y = int(coord_parts[1].strip())
    return (x, y)


def check_starting_position(position_str, maze_obj):
    """
    Check and return the starting position.

    Args:
        position_str (str | None): Position in "x,y" format.
        maze_obj (dict): Maze object with width and height.

    Returns:
        tuple: Valid starting (x, y). Default is (0, 0).
    """
    position = _parse_position(position_str)
    width = maze_obj["width"]
    height = maze_obj["height"]

    if position is None:
        return (0, 0)

    # Check that the position is inside the maze boundaries
    x, y = position
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Starting cell ({x},{y}) is outside maze bounds.")

    return position


def check_goal_position(position_str, maze_obj):
    """
    Check and return the goal position.

    Args:
        position_str (str | None): Position in "x,y" format.
        maze_obj (dict): Maze object with width and height.

    Returns:
        tuple: Valid goal (x, y). Default is (width-1, height-1).
    """
    position = _parse_position(position_str)
    width = maze_obj["width"]
    height = maze_obj["height"]

    if position is None:
        return (width - 1, height - 1)

    x, y = position
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Goal cell ({x},{y}) is outside maze bounds.")

    return position


def remove_loops(path):
    """
    Remove loops from a path by eliminating cycles.

    Args:
        path (list): A list of (x, y, action) tuples.
    Returns:
        list: A cleaned path without loops.
    """
    if not path:
        return path

    cleaned_path = []
    position_indices = {}

    for x, y, action in path:
        position = (x, y)

        # If we've been to this position before we found a loop
        if position in position_indices:
            loop_start = position_indices[position]
            # remove everything from loop and start to now
            cleaned_path = cleaned_path[:loop_start]
            position_indices = {
                p: i for p, i in position_indices.items() if i < loop_start
            }
        #  save this position
        position_indices[position] = len(cleaned_path)
        cleaned_path.append((x, y, action))
    return cleaned_path


def shortest_path(maze_obj, starting=None, goal=None):
    """
    Find the shortest path from starting position to goal.

    Args:
        maze_obj (dict): Maze object.
        starting (tuple, optional): Start (x, y).
        goal (tuple, optional): Goal (x, y).

    Returns:
        list: A list of (x, y, action) tuples that represent the path
    """
    # default start
    if starting is None:
        starting = (0, 0)
    # default goal
    if goal is None:
        width = maze_obj["width"]
        height = maze_obj["height"]
        goal = (width - 1, height - 1)

    # create runner to explore
    explorer = runner.create_runner(starting[0], starting[1], "N")
    explored_path = runner.explore(explorer, maze_obj, goal)
    # remove loops
    cleaned_path = remove_loops(explored_path)
    return cleaned_path


if __name__ == "__main__":
    # command line in argparse
    parser = argparse.ArgumentParser(description="ECS Maze Runner")
    parser.add_argument(
        "maze", help="The name of the maze file, e.g., maze1.mz"
    )
    parser.add_argument(
        "--starting", help='The starting position, e.g., "2, 1"'
    )
    parser.add_argument("--goal", help='The goal position, e.g., "4, 5"')
    args = parser.parse_args()

    # Read and create the maze
    try:
        maze_obj = maze_reader(args.maze)
    except Exception as e:
        print("Error reading maze:", e)
        exit(1)

    try:
        starting = check_starting_position(args.starting, maze_obj)
    except Exception as e:
        print("Invalid starting position:", e)
        exit(1)

    try:
        goal = check_goal_position(args.goal, maze_obj)
    except Exception as e:
        print("Invalid goal position:", e)
        exit(1)

    try:
        path = shortest_path(maze_obj, starting=starting, goal=goal)
    except Exception as e:
        print("Error computing shortest path:", e)
        exit(1)

    # full exploration path
    explorer = runner.create_runner(starting[0], starting[1], "N")
    explored_path = runner.explore(explorer, maze_obj, goal)

    # write the path to csv
    with open("exploration.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Step", "x-coordinate", "y-coordinate", "Actions"])

        for step, (x, y, action) in enumerate(explored_path, start=1):
            writer.writerow([step, x, y, action])

    # calculate Statistics
    exploration_steps = len(explored_path)
    path_length = len(path)
    score = exploration_steps / 4 + path_length

    # results
    print(
        f"Algorithm: Left Hug\n"
        f"Score: {score:.2f}\n"
        f"Exploration steps: {exploration_steps}\n"
        f"Path length: {path_length}"
    )
    # write statistics to file
    with open("statistics.txt", "w", encoding="utf-8") as f:
        f.write(args.maze + "\n")
        f.write(str(score) + "\n")
        f.write(str(exploration_steps) + "\n")
        f.write(str(path) + "\n")
        f.write(str(path_length) + "\n")

    print(path)
