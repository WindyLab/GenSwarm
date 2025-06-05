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
import os
from datetime import datetime

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
        self.formation_points = np.array(formation_points)
        self.target_position = np.array(target_position)
        self.prey_position = None
        self.moveable_objects = []
        self.unexplored_area = []
        self.initial_robot_positions = {}
        self.initial_prey_positions = []
        self.initial_unexplored_area = []
        self.all_robots_id = []
        self.recording = False
        self.recorded_data = []
        self.record_timer = None
        self.flush_timer = None
        self.output_filename = None
        self.last_observation_msg = None

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

    def add_distance_dependent_noise(self, true_value: np.ndarray, distance: float,
                                     sigma0: float = 0.1, alpha: float = 1.0) -> np.ndarray:
        sigma = sigma0 * (1 + alpha * distance)
        noise = np.random.normal(0, sigma, size=true_value.shape)
        return true_value + noise

    def observation_callback(self, msg: Observations):
        self.last_observation_msg = msg
        SIGMA0 = 0.05
        ALPHA = 0.5
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

                pos = np.array([obj.position.x, obj.position.y])
                vel = np.array([obj.velocity.linear.x, obj.velocity.linear.y])
                distance = np.linalg.norm(self.robot_info["position"] - pos)
                if distance > DISTANCE_LIMIT:
                    continue

                noisy_pos = self.add_distance_dependent_noise(pos, distance, SIGMA0, ALPHA)
                noisy_vel = self.add_distance_dependent_noise(vel, distance, SIGMA0, ALPHA)

                self.other_robots_info.append(
                    {
                        "id": obj.id,
                        "position": noisy_pos,
                        "velocity": noisy_vel,
                        "radius": obj.radius,
                    }
                )
            elif obj.type == "Obstacle":
                pos = np.array([obj.position.x, obj.position.y])
                distance = np.linalg.norm(self.robot_info["position"] - pos)
                if distance > DISTANCE_LIMIT:
                    continue

                noisy_pos = self.add_distance_dependent_noise(pos, distance, SIGMA0, ALPHA)

                self.obstacles_info.append(
                    {
                        "id": obj.id,
                        "position": noisy_pos,
                        "radius": obj.radius,
                    }
                )
            elif obj.type == "Prey":
                pos = np.array([obj.position.x, obj.position.y])
                distance = np.linalg.norm(self.robot_info["position"] - pos)
                noisy_pos = self.add_distance_dependent_noise(pos, distance, SIGMA0, ALPHA)
                self.prey_position = noisy_pos

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
        # ✅ 写入记录：每次 observation 时保存一条数据
        if self.recording and self.output_filename:
            import json
            try:
                ts = rospy.Time.now().to_sec()
                raw_obs = []
                for obj in msg.observations:
                    obs_item = {
                        'type': obj.type,
                        'id': obj.id,
                        'position': {'x': obj.position.x, 'y': obj.position.y},
                        'velocity': {
                            'x': obj.velocity.linear.x,
                            'y': obj.velocity.linear.y
                        },
                        'radius': obj.radius
                    }
                    if hasattr(obj, 'color'):
                        obs_item['color'] = obj.color
                    raw_obs.append(obs_item)

                entry = {
                    'timestamp': ts,
                    'self_position': self.robot_info['position'].tolist(),
                    'self_velocity': self.robot_info['velocity'].tolist(),
                    'other_robots': [
                        {
                            'id': r['id'],
                            'pos': r['position'].tolist(),
                            'vel': r['velocity'].tolist(),
                            'rad': r['radius']
                        } for r in self.other_robots_info
                    ],
                    'obstacles': [
                        {
                            'id': o['id'],
                            'pos': o['position'].tolist(),
                            'rad': o['radius']
                        } for o in self.obstacles_info
                    ],
                    'prey_position': self.prey_position.tolist(),
                    'observations': raw_obs
                }

                os.makedirs(os.path.dirname(self.output_filename), exist_ok=True)
                with open(self.output_filename, 'a') as f:
                    print('Writing observation entry to file:', self.output_filename)
                    f.write(json.dumps(entry) + '\n')

            except Exception as e:
                rospy.logerr(f"[Robot {self.robot_id}] Failed to write observation: {e}")

    # 开始录制：启动 10 Hz 定时器
    def start_recording(self, filename):
        print(f"Starting recording at filename: {filename}")
        if not self.recording:
            self.recording = True
            self.recorded_data = []
            self.output_filename = filename

    # 停止录制：关闭定时器，可选保存到 JSON 文件
    def stop_recording(self, filename=None):
        self.record_timer.shutdown()
        self.flush_timer.shutdown()
        self.recording = False
        rospy.loginfo(f"[Robot {self.robot_id}] recording stopped")

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
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            log_file_path = f"/catkin_ws/src/code_llm/logs/run_log_{timestamp}.txt"
            self.start_recording(log_file_path)
            print(f"Initial observations processed successfully")
            self.observation_callback(msg)
            # self.timer = rospy.Timer(rospy.Duration(0.01), self.publish_velocities)

    def publish_velocities(self):
        velocity_msg = Twist()
        velocity_msg.linear.x = self.robot_info["velocity"][0]
        velocity_msg.linear.y = self.robot_info["velocity"][1]
        self.velocity_publisher.publish(velocity_msg)
        # print(f"Published velocity: {self.robot_info['velocity']}")

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


def start_data_recording(filename=None):
    get_current_robot_node().start_recording(filename=None)


def stop_data_recording():
    get_current_robot_node().stop_recording()
