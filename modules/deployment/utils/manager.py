import geometry_msgs

import numpy as np

import rospy
from code_llm.msg import Observations, ObjInfo
from code_llm.srv import (GetTargetPositions, GetTargetPositionsResponse,
                          GetCharPointsResponse, GetCharPoints,
                          ConnectEntities, ConnectEntitiesResponse, ConnectEntitiesRequest)
from geometry_msgs.msg import Twist, Vector3, Point
from modules.deployment.env import EnvironmentBase
from modules.deployment.entity import Robot, Leader

from modules.deployment.utils.char_points_generate import validate_contour_points


class Manager:

    def __init__(self, env: EnvironmentBase):
        self.env = env

        rospy.init_node('simulation_manager', anonymous=True)
        rospy.Subscriber("/leader/velocity", Twist, self.leader_velocity_callback)
        self.observation_publisher = rospy.Publisher(f"observation", Observations, queue_size=1)

        self._pub_list = []
        self._robots = env.get_entities_by_type('Robot')
        robot_start_index = self._robots[0].id
        robot_end_index = self._robots[-1].id
        rospy.set_param("robot_start_index", robot_start_index)
        rospy.set_param("robot_end_index", robot_end_index)
        for i in range(robot_start_index, robot_end_index + 1):
            rospy.Subscriber(
                f"/robot_{i}/velocity", Twist, self.velocity_callback, callback_args=i
            )
        self._target_positions_service = rospy.Service(
            "/get_target_positions", GetTargetPositions, self.get_target_positions_callback
        )
        self._char_points_service = rospy.Service(
            "/get_char_points", GetCharPoints, self.get_char_points_callback
        )

        self._connect_to_service = rospy.Service("/connect_to_others", ConnectEntities,
                                                 self.connect_to_others_callback)
        self._disconnect_service = rospy.Service("/disconnect_from_others", ConnectEntities,
                                                 self.disconnect_from_others_callback)
        self.received_velocity = {robot.id: False for robot in self._robots}

    def velocity_callback(self, data: geometry_msgs.msg.Twist, i):
        """
        velocity_callback is a callback function for the velocity topic.
        """
        desired_velocity = np.array([data.linear.x, data.linear.y])
        print(f"Received velocity for robot {i}: {desired_velocity}")
        self.env.set_entity_velocity(i, desired_velocity)

    def leader_velocity_callback(self, data: Twist):
        leader = self.env.get_entities_by_type('Leader')[0]
        desired_velocity = np.array([data.linear.x, data.linear.y])

        current_velocity = leader.velocity
        dt = 0.01  # assuming a fixed timestep, can be adjusted or calculated dynamically

    def publish_observations(self):
        observation = self.env.get_observation()
        observations_msg = Observations()
        observations_msg.observations = []
        for entity_id, entity in observation.items():
            obj_info = ObjInfo()
            obj_info.id = entity_id
            obj_info.position = Point(x=entity["position"][0], y=entity["position"][1], z=0)
            obj_info.velocity = Twist(linear=Vector3(x=entity["velocity"][0], y=entity["velocity"][1], z=0),
                                      angular=Vector3(x=0, y=0, z=0))
            obj_info.radius = entity["size"] if isinstance(entity["size"], float) else 0.0
            obj_info.type = entity["type"]
            if entity["target_position"] is not None:
                obj_info.target_position = Point(x=entity["target_position"][0], y=entity["target_position"][1], z=0)
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
            obj_info.position = Point(x=robot.target_position[0], y=robot.target_position[1], z=0)
            response.target_positions.append(obj_info)
        return response

    def get_char_points_callback(self, request):
        char = request.character
        sampled_points = validate_contour_points(char)

        response = GetCharPointsResponse()
        for point in sampled_points:
            pt = Point(x=int(point[0]), y=int(point[1]), z=0)
            response.points.append(pt)

        return response

    def connect_to_others_callback(self, request: ConnectEntitiesRequest):
        response = ConnectEntitiesResponse()
        result = self.env.connect_to(entity1_id=request.self_id, entity2_id=request.target_id)
        response.success = result
        return response

    def disconnect_from_others_callback(self, request: ConnectEntitiesRequest):
        response = ConnectEntitiesResponse()
        result = self.env.disconnect_entities(entity1_id=request.self_id, entity2_id=request.target_id)
        response.success = result
        return response
