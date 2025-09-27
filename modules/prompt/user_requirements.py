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
    "crossing": "Each robot must maintain a distance of at least fifteen centimeters from other robots and obstacles to avoid collisions while moving to the target point, which is the position of the robot that was farthest from it at the initial moment.The local control law uses ORCA",
    "shaping": "The robots need to form a specific shape, with each robot assigned a unique point on that shape to move to while avoiding collisions during the movement.",
    "encircling": "The robots need to be evenly distributed along a circle with a one-unit radius, centered on the prey. Each robot is assigned a specific angle. As the prey moves, the robots must continuously adjust their positions in real-time, responding to the prey's dynamic changes. This ensures a sustained and coordinated encirclement.",
    "exploration": "The robots need to explore all the unknown areas. You are required to assign an optimal sequence of exploration areas to each robot based on the number of robots and the unexplored regions, and then the robots will gradually explore these areas.",
    "clustering": "Robots with initial positions in the same quadrant need to cluster in the designated area of that corresponding quadrant.",
    "pursuing": "Engage in flocking behavior with all robots on the map, moving toward the lead robot. The lead robot's movement is unpredictable, so maintain cohesion by staying connected, ensure alignment by moving in sync, and uphold separation by keeping a safe personal space. Additionally, be cautious to avoid collisions with any obstacles in the environment.",
}

task_prompts = {
    "encircling": {
        "default": "The robots need to be evenly distributed along a circle with a one-unit radius, centered on the prey. Each robot is assigned a specific angle. As the prey moves, the robots must continuously adjust their positions in real-time, responding to the prey's dynamic changes. This ensures a sustained and coordinated encirclement.",
        "compound": "Robots maintain a coordinated circular formation around the moving prey, evenly spaced at a one-unit radius with real-time position adjustments. Each robot is assigned a predefined angle and continuously tracks the corresponding point on a unit circle centered at the prey's moving position.",
        "simple": "Robots maintain a coordinated circular formation around the moving prey, evenly spaced at a one-unit radius with real-time position adjustments.",
        "simple_strategy": "Each robot is assigned a predefined angle and continuously tracks the corresponding point on a unit circle centered at the prey's moving position.",
        "narrative": (
            "Imagine a pack of robots encircling their prey like wolves hunting, "
            "fluidly adjusting their formation while maintaining a strict one-meter distance. "
            "They are evenly distributed around the prey, each occupying a precise angular position. "
            "Each robot autonomously finds the optimal spot on this invisible perimeter, "
            "moving in perfect coordination along the circular path just an arm’s length from the target, "
            "their synchronized motion dynamically mirroring every shift in the prey’s trajectory."
        ),
        "structured_strategy": (
            "[Task Description]: Each robot is assigned a predefined angle and continuously tracks the corresponding point on a unit circle centered at the prey's moving position.\n"
            "[Optimization Objective]:\n"
            "• Minimize the overall formation error while maintaining real-time encirclement of the moving target\n"
            "[Constraints]:\n"
            "1. Strictly maintain a 1-meter encirclement radius\n"
            "2. Even angular spacing betn robots\n"
            "3. Dynamically move based on the target's position\n"
        ),
        "structured_default": (
            "[Task Description]: Robots maintain a coordinated circular formation around the moving prey, evenly spaced at a one-unit radius with real-time position adjustments.\n"
            "[Optimization Objective]:\n"
            "• Minimize the overall formation error while maintaining real-time encirclement of the moving target\n"
            "[Constraints]:\n"
            "1. Strictly maintain a 1-meter encirclement radius\n"
            "2. Even angular spacing between robots\n"
            "3. Dynamically move based on the target's position\n"
        ),
    },
    "shaping": {
        "default": "The robots need to form a specific shape, with each robot assigned a unique point on that shape to move to while avoiding collisions during the movement.",
        "compound": "Robots move to form a specific shape, with real-time collision avoidance during the process.Each robot is assigned a unique target position and moves to it while avoiding collisions.",
        "simple": "Robots move to form a specific shape, with real-time collision avoidance during the process.",
        "simple_strategy": "Each robot is assigned a unique target position and moves to it while avoiding collisions.",
        "narrative": (
            "Like a drone light show in the night sky, each robot follows a predefined path to reach its precise position within the formation. "
            "Together, they assemble a cleaweerly recognizable geometric pattern. "
            "Throughout the movement, they maintain safe distances and avoid collisions, "
            "ultimately forming a stable and orderly spatial configuration."
        ),
        "structured_default": (
            "[Task Description]: Robots move to form a specific shape, with real-time collision avoidance during the process.\n",
            "[Optimization Objective]:\n"
            "• Minimize the total time or total path length required to reach the target shape\n"
            "[Constraints]:\n"
            "1. Each robot must be assigned a unique target position to ensure complete shape coverage\n"
            "2. No collisions are allowed during movement\n"
            "3. Robots must remain stationary or make fine adjustments after reaching the target to maintain formation precision\n"
        ),
        "structured_strategy": (
            "[Task Description]: Each robot is assigned a unique target position and moves to it while avoiding collisions.\n"
            "[Optimization Objective]:\n"
            "• Minimize the total time or total path length required to reach the target shape\n"
            "[Constraints]:\n"
            "1. Each robot must be assigned a unique target position to ensure complete shape coverage\n"
            "2. No collisions are allowed during movement\n"
            "3. Robots must remain stationary or make fine adjustments after reaching the target to maintain formation precision\n"
        )
    },
    "covering": {
        "default": "Divide the environment into sections equal to the number of robots. Each robot needs to move to the center of its assigned section to achieve full coverage of the environment.",
        "simple": "Robots should be evenly distributed across the environment to achieve full coverage.",
        "compound": "Robots should be evenly distributed across the environment to achieve full coverage. Divide the environment into equal-sized grid cells based on the number of robots. Assign each robot to a grid cell and have it move to the center.",
        "narrative": (
            "Like sentinels stationed at fixed posts, robots are evenly deployed to their designated regions. "
            "They move to the center of each area and remain in position, "
            "forming a seamless sensing network that ensures every part of the environment is within monitoring range."
        ),
        "simple_strategy": "Divide the environment into equal-sized grid cells based on the number of robots. Assign each robot to a grid cell and have it move to the center.",
        "structured_default": (
            "[Task Description]: Robots should be evenly distributed across the environment to achieve full coverage.\n"
            "[Optimization Objective]:\n"
            "• Minimize the total travel distance of all robots\n"
            "[Constraints]:\n"
            "1. Each robot must be assigned a distinct region center, and regions must not overlap\n"
            "2. All regions combined must fully cover the environment\n"
            "3. Robots should be evenly distributed within the environment to ensure uniform coverage density\n"
        ),
        "structured_strategy": (
            "[Task Description]: Divide the environment into equal-sized grid cells based on the number of robots. Assign each robot to a grid cell and have it move to the center.\n"
            "[Optimization Objective]:\n"
            "• Minimize the total travel distance of all robots\n"
            "[Constraints]:\n"
            "1. Each robot must be assigned a distinct region center, and regions must not overlap\n"
            "2. All regions combined must fully cover the environment\n"
            "3. Robots should be evenly distributed within the environment to ensure uniform coverage density\n"
        )
    },
    "crossing": {
        "default": "Each robot must maintain a distance of at least fifteen centimeters from other robots and obstacles to avoid collisions while moving to the target point, which is the position of the robot that was farthest from it at the initial moment.The local control law uses ORCA implemented via the RVO2 library.",
    }

}


def get_user_commands(task_name: str | list = None, format_type: str = 'simple_strategy') -> list[str]:
    """
    Retrieve user command prompts for specified tasks in various formats.

    Args:
        task_name (str or list of str, optional): Name(s) of the task(s) to retrieve prompts for.
            If None, prompts for all tasks are returned.
        format_type (str): The format of the prompt. Options:
            - 'default': Original task description from the tasks dict
            - 'narrative': Natural language storytelling format
            - 'structured': Parameterized task specification template
            - 'step': Step-by-step algorithm flow

    Returns:
        list[str]: A list of prompt strings corresponding to each requested task.

    Raises:
        ValueError: If task_name is not None, str, or list of str.
        KeyError: If a requested task_name is not found in task_prompts.
    """
    # Determine the list of task names to process
    if task_name is None:
        names = list(task_prompts.keys())
    elif isinstance(task_name, str):
        names = [task_name]
    elif isinstance(task_name, list):
        names = task_name
    else:
        raise ValueError("task_name must be None, a string, or a list of strings")

    results = []
    for name in names:
        prompts = task_prompts.get(name)
        if prompts is None:
            raise KeyError(f"Unknown task: {name}")
        # Select the prompt for the requested format, fallback to default if unavailable
        text = prompts.get(format_type)
        results.append(text)

    return results


def get_commands_name() -> list[str]:
    """
    Description: Get the names of the user commands to be implemented.
    Returns:
        list[str]: The list of names of user commands to be implemented.
    """
    return list(tasks.keys())
