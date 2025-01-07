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

import numpy as np
import rospy
import threading

from geometry_msgs.msg import Twist
from code_llm.msg import Observations

robot_nodes = {}
thread_local = threading.local()


class RobotNode:
    def __init__(
            self, robot_id, target_position=None, formation_points=None, assigned_task=None
    ):
        self.robot_id = robot_id
        self.assigned_task = assigned_task
        self.ros_initialized = False
        self.velocity_publisher = None
        self.robot_info = {
            "position": np.array([0.0, 0.0]),
            "radius": 0.0,
            "velocity": np.array([0.0, 0.0]),
        }
        self.quadrant_target_position = {
            3: np.array([-1.25, -1.25]),
            2: np.array([-1.25, 1.25]),
            1: np.array([1.25, 1.25]),
            4: np.array([1.25, -1.25]),
        }
        self.timer = None
        self.init_position = None
        self.target_position = None
        self.obstacles_info = []
        self.other_robots_info = []
        formation_points = [(0, -1), (0, 1), (-1, 0), (0, 0), (1, 0)]
        self.formation_points = np.array(formation_points)
        self.target_position = np.array(target_position)
        self.prey_position = None
        self.moveable_objects = []
        self.unexplored_area = []
        self.initial_robot_positions = {}
        self.initial_prey_positions = []
        self.initial_unexplored_area = []
        self.all_robots_id = []

    def process_initial_observations(self, msg: Observations):
        self.initial_robot_positions = {}
        self.initial_prey_positions = []
        self.initial_unexplored_area = []
        self.all_robots_id = []

        for obj in msg.observations:
            if obj.type == "Robot":
                position = np.array([obj.position.x, obj.position.y])
                self.initial_robot_positions[obj.id] = position
                self.all_robots_id.append(obj.id)
                if obj.id == self.robot_id:
                    self.robot_info["position"] = position
                    if self.init_position is None:
                        self.init_position = self.robot_info["position"]
                    self.robot_info["radius"] = obj.radius
            elif obj.type == "Prey":
                position = np.array([obj.position.x, obj.position.y])
                self.initial_prey_positions.append(position)
            elif obj.type == "Landmark" and obj.color == "gray":
                self.initial_unexplored_area.append(
                    {
                        "id": len(self.initial_unexplored_area),
                        "position": np.array([obj.position.x, obj.position.y]),
                    }
                )

    def observation_callback(self, msg: Observations):
        self.obstacles_info = []
        self.other_robots_info = []
        self.prey_positions = []
        self.moveable_objects = []
        self.unexplored_area = []
        for obj in msg.observations:
            # Robot's perception distance limit
            DISTANCE_LIMIT = 1.0
            if obj.type == "Robot":
                if obj.id == self.robot_id:
                    self.robot_info["position"] = np.array(
                        [obj.position.x, obj.position.y]
                    )
                    if self.init_position is None:
                        self.init_position = self.robot_info["position"]
                    self.robot_info["radius"] = obj.radius
                    continue

                # Calculate distance to the current robot
                distance = np.linalg.norm(
                    self.robot_info["position"]
                    - np.array([obj.position.x, obj.position.y])
                )
                if distance > DISTANCE_LIMIT:
                    continue

                self.other_robots_info.append(
                    {
                        "id": obj.id,
                        "position": np.array([obj.position.x, obj.position.y]),
                        "velocity": np.array(
                            [obj.velocity.linear.x, obj.velocity.linear.y]
                        ),
                        "radius": obj.radius,
                    }
                )
            elif obj.type == "Obstacle":
                # Calculate distance to the current robot
                distance = np.linalg.norm(
                    self.robot_info["position"]
                    - np.array([obj.position.x, obj.position.y])
                )
                if distance > DISTANCE_LIMIT:
                    continue

                self.obstacles_info.append(
                    {
                        "id": obj.id,
                        "position": np.array([obj.position.x, obj.position.y]),
                        "radius": obj.radius,
                    }
                )
            elif obj.type == "Prey":
                self.prey_position = np.array([obj.position.x, obj.position.y])
            elif obj.type == "Landmark":
                if obj.color == "gray":
                    distance = np.linalg.norm(
                        self.robot_info["position"]
                        - np.array([obj.position.x, obj.position.y])
                    )
                    if distance > DISTANCE_LIMIT:
                        continue
                    self.unexplored_area.append(
                        {
                            "id": len(self.unexplored_area),
                            "position": np.array([obj.position.x, obj.position.y]),
                        }
                    )

    def initialize_ros_node(self):
        if not self.ros_initialized:
            self.ros_initialized = True
            rospy.Subscriber(f"/observation", Observations, self.observation_callback)
            self.velocity_publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

            print(
                f"Waiting for position message from /robot_{self.robot_id}/observation..."
            )
            msg = rospy.wait_for_message(f"/observation", Observations)
            self.process_initial_observations(msg)
            print(f"Initial observations processed successfully")
            self.observation_callback(msg)
            # self.timer = rospy.Timer(rospy.Duration(0.01), self.publish_velocities)

    def publish_velocities(self):
        velocity_msg = Twist()
        velocity_msg.linear.x = self.robot_info["velocity"][0]
        velocity_msg.linear.y = self.robot_info["velocity"][1]
        self.velocity_publisher.publish(velocity_msg)

    def get_all_target_areas(self):
        return self.unexplored_area

    def get_self_position(self):
        return self.robot_info["position"]

    def get_self_velocity(self):
        return self.robot_info["velocity"]

    def get_self_radius(self):
        return self.robot_info["radius"]

    def set_self_velocity(self, velocity):
        self.robot_info["velocity"] = np.array(velocity)
        self.publish_velocities()

    def get_surrounding_robots_info(self):
        return self.other_robots_info

    def get_surrounding_obstacles_info(self):
        return self.obstacles_info

    def get_prey_position(self):
        return self.prey_position

    def get_sheep_positions(self):
        return self.prey_positions

    def get_self_id(self):
        return self.robot_id

    def get_all_robots_id(self):
        return self.all_robots_id

    def get_target_position(self):
        return self.target_position

    def get_target_formation_points(self):
        return self.formation_points

    def get_unexplored_area(self):
        return self.unexplored_area

    def get_quadrant_target_position(self):
        return self.quadrant_target_position

    def get_all_robots_initial_position(self):
        return self.initial_robot_positions

    def get_prey_initial_position(self):
        return self.initial_prey_positions

    def get_initial_unexplored_area(self):
        return self.initial_unexplored_area

    def get_assigned_task(self):
        return self.assigned_task


def set_current_robot_id(robot_id, **kwargs):
    thread_local.robot_id = robot_id
    if robot_id not in robot_nodes:
        robot_nodes[robot_id] = RobotNode(robot_id, **kwargs)
    robot_nodes[robot_id].initialize_ros_node()


def get_current_robot_node():
    robot_id = getattr(thread_local, "robot_id", None)
    if robot_id is None:
        raise ValueError("No robot_id is set for the current thread")
    return robot_nodes[robot_id]


def initialize_ros_node(robot_id, **kwargs):
    set_current_robot_id(robot_id, **kwargs)


def get_self_position():
    return get_current_robot_node().get_self_position()


def get_self_velocity():
    return get_current_robot_node().get_self_velocity()


def get_self_radius():
    return get_current_robot_node().get_self_radius()


def set_self_velocity(velocity):
    get_current_robot_node().set_self_velocity(velocity)


def get_surrounding_robots_info():
    return get_current_robot_node().get_surrounding_robots_info()


def get_surrounding_obstacles_info():
    return get_current_robot_node().get_surrounding_obstacles_info()


def get_sheep_positions():
    return get_current_robot_node().get_sheep_positions()


def get_surrounding_unexplored_area():
    return get_current_robot_node().get_unexplored_area()


def get_prey_position():
    return get_current_robot_node().get_prey_position()


def get_lead_position():
    return get_current_robot_node().get_prey_position()


def get_environment_range():
    return {"x_min": -2.5, "x_max": 2.5, "y_min": -2.5, "y_max": 2.5}


def stop_self():
    get_current_robot_node().set_self_velocity([0, 0])


def get_self_id():
    return get_current_robot_node().get_self_id()


def get_target_position():
    return get_current_robot_node().get_target_position()


def get_surrounding_unexplored_area():
    return get_current_robot_node().get_surrounding_unexplored_area()


def get_surrounding_environment_info():
    node = get_current_robot_node()
    surrounding_robots = node.get_surrounding_robots_info()
    surrounding_obstacles = node.get_surrounding_obstacles_info()

    # Create a list to store the information of the surrounding environment
    environment_info = []

    # Add robots' information to the list
    for robot in surrounding_robots:
        environment_info.append(
            {
                "Type": "robot",
                "position": robot["position"],
                "velocity": robot["velocity"],
                "radius": robot["radius"],
            }
        )

    # Add obstacles' information to the list
    for obstacle in surrounding_obstacles:
        environment_info.append(
            {
                "Type": "obstacle",
                "position": obstacle["position"],
                "velocity": np.array([0, 0]),  # Obstacles don't move
                "radius": obstacle["radius"],
            }
        )

    return environment_info


def get_target_formation_points():
    return get_current_robot_node().get_target_formation_points()


def get_quadrant_target_position():
    return get_current_robot_node().get_quadrant_target_position()


def get_assigned_task():
    return get_current_robot_node().get_assigned_task()
