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
import time

import rospy
from code_llm.msg import Observations
import numpy as np
from code_llm.srv import GetCharPoints, GetCharPointsRequest

initial_robot_positions = {}
initial_prey_position = []
initial_unexplored_areas = []
all_robots_id = []
init = False


def process_initial_observations(msg: Observations):
    global initial_robot_positions, initial_prey_position, initial_unexplored_area, all_robots_id
    print("Processing initial observations...")
    initial_robot_positions.clear()
    initial_unexplored_areas.clear()
    all_robots_id.clear()

    for obj in msg.observations:
        if obj.type == "Robot":
            position = np.array([obj.position.x, obj.position.y])
            initial_robot_positions[obj.id] = position
            all_robots_id.append(obj.id)
        elif obj.type == "Prey":
            position = np.array([obj.position.x, obj.position.y])
            initial_prey_position = position
        elif obj.type == "Landmark" and obj.color == "gray":
            initial_unexplored_areas.append(np.array([obj.position.x, obj.position.y]))


def init_node():
    global init
    if init:
        return
    init = True
    print("Waiting for initial observations...")
    rospy.Subscriber("/observation", Observations, process_initial_observations)
    msg = rospy.wait_for_message("/observation", Observations)
    process_initial_observations(msg)
    print("Initial observations received.")


def get_all_robots_initial_position():
    init_node()
    return initial_robot_positions


def get_prey_initial_position():
    init_node()
    return initial_prey_position


def get_initial_unexplored_areas():
    init_node()
    return initial_unexplored_areas


def get_environment_range():
    init_node()
    return {"x_min": -2.5, "x_max": 2.5, "y_min": -2.5, "y_max": 2.5}


def get_contour_points(character):
    init_node()
    rospy.wait_for_service("/get_char_points")
    try:
        get_char_points = rospy.ServiceProxy("/get_char_points", GetCharPoints)
        request = GetCharPointsRequest(character=character)
        response = get_char_points(request)
        points = [(point.x, point.y) for point in response.points]
        return points
    except rospy.ServiceException as e:
        print(f"Service call failed: {e}")
        return []


def get_target_formation_points():
    init_node()

    target_shape = [
        np.array((1, -1)),
        np.array((1, 1)),
        np.array((0, 0)),
        np.array((1, 0)),
        np.array((2, 0)),
    ]
    return target_shape


def get_quadrant_target_position():
    init_node()

    quadrant_target_position = {
        3: np.array([-1.25, -1.25]),
        2: np.array([-1.25, 1.25]),
        1: np.array([1.25, 1.25]),
        4: np.array([1.25, -1.25]),
    }

    return quadrant_target_position


def get_all_robots_id():
    init_node()
    return all_robots_id
