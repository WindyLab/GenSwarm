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
    "bridging": "The robots need to evenly form a straight line bridge at the position where x is equal to zero within the range of y between minus two and two.",
    "flocking": "Integrate into a flock by collaborating with all robots within the map, ensuring cohesion by staying connected, alignment by moving together, and separation by keeping a safe distance.",
    "covering": "Divide the environment into sections equal to the number of robots. Each robot needs to move to the center of its assigned section to achieve full coverage of the environment.",
    "aggregation": "The robots need to aggregate as quickly as possible and avoid colliding with each other.",
    "crossing": "Each robot must maintain a distance of at least fifteen centimeters from other robots and obstacles to avoid collisions while moving to the target point, which is the position of the robot that was farthest from it at the initial moment.",
    "shaping": "The robots need to form a specific shape, with each robot assigned a unique point on that shape to move to while avoiding collisions during the movement.",
    "encircling": "The robots need to be evenly distributed along a circle with a one-unit radius, centered on the prey. Each robot is assigned a specific angle. As the prey moves, the robots must continuously adjust their positions in real-time, responding to the prey's dynamic changes. This ensures a sustained and coordinated encirclement.",
    "exploration": "The robots need to explore all the unknown areas. You are required to assign an optimal sequence of exploration areas to each robot based on the number of robots and the unexplored regions, and then the robots will gradually explore these areas.",
    "clustering": "Robots with initial positions in the same quadrant need to cluster in the designated area of that corresponding quadrant.",
    "pursuing": "Engage in flocking behavior with all robots on the map, moving toward the lead robot. The lead robot's movement is unpredictable, so maintain cohesion by staying connected, ensure alignment by moving in sync, and uphold separation by keeping a safe personal space. Additionally, be cautious to avoid collisions with any obstacles in the environment.",
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
