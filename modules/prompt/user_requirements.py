"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""

tasks = {
    "bridging": "The robots need to evenly form a straight line bridge at the position where x=0 within the range of −2<y<2.",
    "flocking": "Integrate into a flock by collaborating with all robots within the map, ensuring cohesion by staying connected, alignment by moving together, and separation by keeping at least 0.5 meters apart.",
    "covering": "Evenly sample target positions across the entire map, then assign the corresponding position based on each robot's ID.",
    "circling": "The robots need to be evenly distributed on a circle with a radius of 1 centered at (0,0).",
    "crossing": "Each robot must maintain a distance of at least 0.15 meters from other robots and obstacles to avoid collisions while moving to the target point, which is the position of the robot that was farthest from it at the initial moment.",
    "shaping": "The robots need to form a specific shape, with each robot assigned a unique point on that shape to move to while avoiding collisions during the movement.",
    "encircling": "The robots need to surround the target prey by evenly distributing themselves along a circle with a radius of 1, centered on the prey, with each robot assigned a specific angle, and adjust their positions in real-time based on the prey's movement to achieve coordinated encirclement.",
    "exploration": "The robots need to collaboratively explore an unknown area. You are required to assign an optimal sequence of exploration areas to each robot based on the number of robots and the unexplored areas.",
    "clustering": "Robots with initial positions in the same quadrant need to cluster in the designated area of that corresponding quadrant.",
    "pursuing": "The robots need to pursue the target prey by moving towards the prey's position while avoiding collisions with other robots and obstacles.",
}


def get_user_commands(task_name: str | list = None) -> list[str]:
    """
    Description: Get the user commands to be implemented.
    Args:
        task_name: str|list, the name of the task to be implemented (default is None).
        options are ["flocking", "covering", "exploration", "pursuit", "crossing", "shaping", None]
        When task_name is None, return all the user commands.
    Returns:
        list[str]: The list of user commands to be implemented.
    """

    if task_name is None:
        return list(tasks.values())
    elif isinstance(task_name, str):
        return [tasks[task_name]]
    elif isinstance(task_name, list):
        return [tasks[task] for task in task_name]


def get_commands_name() -> list[str]:
    """
    Description: Get the names of the user commands to be implemented.
    Returns:
        list[str]: The list of names of user commands to be implemented.
    """
    return list(tasks.keys())
