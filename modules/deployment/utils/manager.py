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
import traceback
from traceback import TracebackException

import geometry_msgs

import numpy as np

import rospy
from code_llm.msg import Observations, ObjInfo
from code_llm.srv import (
    GetTargetPositions,
    GetTargetPositionsResponse,
    GetCharPointsResponse,
    GetCharPoints,
    ConnectEntities,
    ConnectEntitiesResponse,
    ConnectEntitiesRequest,
)
from geometry_msgs.msg import Twist, Vector3, Point
from modules.deployment.utils.char_points_generate import validate_contour_points


class Manager:
    def __init__(self, env, max_speed=1.2, real=False):
        self.last_time = 0
        self.env = env
        if not real:
            rospy.init_node("simulation_manager", anonymous=True)
        self._pub_list = []
        self._robots = env.get_entities_by_type("Robot") + env.get_entities_by_type(
            "Leader"
        )
        self._max_speed = max_speed
        robot_start_index = min(self._robots, key=lambda x: x.id).id
        robot_end_index = max(self._robots, key=lambda x: x.id).id
        rospy.set_param("robot_start_index", robot_start_index)
        rospy.set_param("robot_end_index", robot_end_index)

        for i in range(robot_start_index, robot_end_index + 1):
            rospy.Subscriber(
                f"/robot_{i}/velocity",
                Twist,
                self.velocity_callback,
                callback_args=i,
                queue_size=1,
            )
        rospy.Subscriber("/leader/velocity", Twist, self.leader_velocity_callback)
        try:
            self._target_positions_service = rospy.Service(
                "/get_target_positions",
                GetTargetPositions,
                self.get_target_positions_callback,
            )
            self._char_points_service = rospy.Service(
                "/get_char_points", GetCharPoints, self.get_char_points_callback
            )
        except Exception as e:
            pass
        self.observation_publisher = rospy.Publisher(
            f"observation", Observations, queue_size=1
        )

        self.robotID_velocity = {
            robot.id: np.array([0, 0], dtype=float) for robot in self._robots
        }

    def velocity_callback(self, data: geometry_msgs.msg.Twist, i):
        """
        velocity_callback is a callback function for the velocity topic.
        """
        # current_time = time.time()
        # time_diff = current_time - self.last_time
        #
        # # 计算频率
        # if time_diff > 0:
        #     frequency = 1 / time_diff
        #     print(f"Frequency: {frequency:.2f} Hz")
        #
        # self.last_time = current_time
        desired_velocity = (
            np.array([data.linear.x, data.linear.y])
            / (np.linalg.norm([data.linear.x, data.linear.y]) + 0.001)
            * self._max_speed
        )
        # print(f"Received velocity for robot {i}: {desired_velocity}")
        self.robotID_velocity[i] = desired_velocity
        # self.env.set_entity_velocity(i, desired_velocity)

    def leader_velocity_callback(self, data: Twist):
        leader = self.env.get_entities_by_type("Leader")
        if len(leader) == 0:
            if len(self.env.get_entities_by_type("Prey")) > 0:
                leader = self.env.get_entities_by_type("Prey")[0]
            elif len(self._robots) > 0:
                leader = self._robots[0]
        else:
            leader = leader[0]
        desired_velocity = np.array([data.linear.x, data.linear.y])
        self.env.set_entity_velocity(entity_id=leader.id, velocity=desired_velocity)

    def publish_observations(self, obs=None):
        if obs:
            observation = obs
        else:
            observation = self.env.get_observation()
        observations_msg = Observations()
        observations_msg.observations = []
        for entity_id, entity in observation.items():
            obj_info = ObjInfo()
            obj_info.id = entity_id
            obj_info.position = Point(
                x=entity["position"][0], y=entity["position"][1], z=0
            )
            obj_info.velocity = Twist(
                linear=Vector3(x=entity["velocity"][0], y=entity["velocity"][1], z=0),
                angular=Vector3(x=0, y=0, z=0),
            )
            obj_info.radius = (
                entity["size"] if isinstance(entity["size"], float) else 0.0
            )
            obj_info.type = entity["type"]
            if entity["target_position"] is not None:
                obj_info.target_position = Point(
                    x=entity["target_position"][0], y=entity["target_position"][1], z=0
                )
            obj_info.color = entity["color"]
            observations_msg.observations.append(obj_info)
        self.observation_publisher.publish(observations_msg)

    def get_target_positions_callback(self, request):
        response = GetTargetPositionsResponse()
        for robot in self._robots:
            obj_info = ObjInfo()
            obj_info.id = robot.id
            if robot.target_position is None:
                robot.target_position = np.array([0, 0])
            obj_info.position = Point(
                x=robot.target_position[0], y=robot.target_position[1], z=0
            )
            response.target_positions.append(obj_info)
        return response

    def get_char_points_callback(self, request):
        char = request.character
        try:
            sampled_points = validate_contour_points(char)
        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()

        response = GetCharPointsResponse()
        for point in sampled_points:
            pt = Point(x=point[1], y=point[0], z=0)
            response.points.append(pt)
        return response

    def clear_velocity(self):
        self.robotID_velocity = {
            robot.id: np.array([0, 0], dtype=float) for robot in self._robots
        }
