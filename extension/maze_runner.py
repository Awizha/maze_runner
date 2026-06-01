"""
MAZE RUNNER - EXTENSION WITH BFS ALGORITHM.

This extension implements a Breadth-First Search (BFS) algorithm to solve
the maze.

BFS ALGORITHM EXPLANATION:
The BFS algorithm explores the maze in a structered way by visiting cells
level-by-level. This guarantees that the first time the goal is reached,
the path found is the shortest possible. Unlike the left-hug algorithm,
which follows walls and spends a lot of time backtracking.

The BFS algorithm
- Uses a queue to explore cells in order of distance from starting position
- Keeps track of visited cells so the same position is not explored
  multiple times
- Stops as soon as the goal is reached
- Reconstructs the best path by tracing back through perviously visited
  cells
- Only exploring cells that are needed to determine the shortest path

Since BFS explores fewer cells, the final score is lower, which means it
performs better.

This results in significantly better scores (lower is better).
Score formula: exploration_steps / 4 + path_length
"""

__author__ = "Awizha Abroon"
__created__ = "December 5, 2025"

import argparse
import csv
import maze
from collections import deque


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

    # Check all lines have the same length
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
    # Convert the input string "x,y" into a tuple (x, y)
    position = _parse_position(position_str)

    # get maze size
    width = maze_obj["width"]
    height = maze_obj["height"]

    if position is None:
        return (width - 1, height - 1)
    # extract x and y
    x, y = position

    # check that the goal is inside the maze boundaries
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Goal cell ({x},{y}) is outside maze bounds.")

    return position


def get_action_between_cells(from_pos, to_pos):
    """
    Determine the action needed to move from one cell to the next.

    The two cells must be next to each other (no diagonal movement).

    Args:
        from_pos (tuple): Current position (x, y).
        to_pos (tuple): Target position (x, y).

    Returns:
        str: Action string ('F', 'B', 'RF', 'LF').
    """
    # Current position
    fx, fy = from_pos

    # Target position
    tx, ty = to_pos

    # If the target cell is to the right, move east
    if tx == fx + 1:
        return "RF"

    # If the target cell is to the left, move west
    elif tx == fx - 1:
        return "LF"

    # If the target cell is above, move north
    elif ty == fy + 1:
        return "F"

    # If the target cell is below, move south
    elif ty == fy - 1:
        return "B"

    # Default
    else:
        return "F"


def bfs_explore(maze_obj, starting, goal):
    """
    Perform Breadth-First Search to find the shortest path.

    BFS is a suitable algorithm for finding the shortest path in tree
    and graph structures. It works by exploring all neighbouring cells
    at the current distance from the starting position before moving on
    to cells that are further away.

    Args:
        maze_obj: The maze dictionary
        starting: Starting position (x, y)
        goal: Goal position (x, y)

    Returns:
        explored_path: List of (x, y, action) tuples representing steps
                       taken during exploration

    Algorithm:
        1. Begins queue from the starting position
        2. Keep Track of visited cells and their parent cells
        3. Checks all possible directions (North, East, South, West)
           for each cell
        4. Adds unvisited neighboring cells to the queue
        5. Stops the search once the goal is reached
        6. Reconstruct shortest path from goal to starting position
           using parent pointers

    Key Advantage:
        BFS explores the maze level by level, meaning all cells at a
        given distance are visited before moving to the next level.
        This guarantees that the shortest path is found while avoiding
        unnecessary backtracking.
    """
    from maze import get_walls

    # Queue BFS (starting cell)
    queue = deque([starting])

    # Tracks visited cells
    visited_cells = {starting}

    # Store where each cell came from
    parent = {starting: None}

    # Explore until the queue is empty
    while queue:
        current = queue.popleft()

        # Stop when goal is reached
        if current == goal:
            break

        x, y = current

        # Check which walls exist around the current cell
        north, east, south, west = get_walls(maze_obj, x, y)

        # possible moves
        directions = [
            ((x, y + 1), not north),  # North
            ((x + 1, y), not east),  # East
            ((x, y - 1), not south),  # South
            ((x - 1, y), not west),  # West
        ]
        # Add all the valid and unvisited neigbour cells
        for next_pos, is_open in directions:
            if is_open and next_pos not in visited_cells:
                visited_cells.add(next_pos)
                parent[next_pos] = current
                queue.append(next_pos)

    # If the goal is not reached it means no valid path
    if goal not in parent:
        raise ValueError("No path found to goal.")

    # Reconstruct the shortest path by following the parent links
    # (goal->start)
    shortest_path_cells = []
    current = goal

    # Follow the parent links backwards from goal to start
    while parent[current] is not None:
        shortest_path_cells.append(current)
        current = parent[current]

    # Add the starting cell (it has no parent)
    shortest_path_cells.append(starting)

    # Reverse the list (start -> goal)
    shortest_path_cells.reverse()

    # Convert the path from a list to (x, y, action) format
    path_with_actions = []

    # For each pair of cells in the path
    for i in range(len(shortest_path_cells) - 1):
        from_cell = shortest_path_cells[i]
        to_cell = shortest_path_cells[i + 1]
        # Determine the action (North/East/South/West) moves from
        # from_cell to to_cell
        action = get_action_between_cells(from_cell, to_cell)
        # add the coordinates and actions to the result
        path_with_actions.append((from_cell[0], from_cell[1], action))

    return path_with_actions


def shortest_path(maze_obj, starting=None, goal=None):
    """
    Find the shortest path using BFS algorithm.

    Args:
        maze_obj: The maze object
        starting: Starting position (x, y), defaults to (0, 0)
        goal: Goal position (x, y), defaults to top-right corner

    Returns:
        path: List of (x, y, action) tuples representing the path
    """
    # Set defaults
    if starting is None:
        starting = (0, 0)

    if goal is None:
        width = maze_obj["width"]
        height = maze_obj["height"]
        goal = (width - 1, height - 1)

    # Use BFS algorithm
    path = bfs_explore(maze_obj, starting, goal)

    return path


if __name__ == "__main__":
    # command line in argparse
    parser = argparse.ArgumentParser(
        description="ECS Maze Runner - BFS Extension"
    )
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

    # checks and parse the starting position
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

    # For BFS, the exploration path equals the solution path
    explored_path = path

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
        f"Algorithm: BFS\n"
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
