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

import json
import rospy
from geometry_msgs.msg import PoseStamped, TwistStamped
from sensor_msgs.msg import Joy
from std_msgs.msg import Bool
import numpy as np
import socket
import os
import time
import threading
from scipy.spatial.transform import Rotation as R
from sympy import euler

from .base_engine import Engine

from code_llm.msg import Observations
from rospy_message_converter import json_message_converter

from modules.deployment.utils.mqtt_pub import MqttClientThread


class OmniEngine(Engine):
    def __init__(self):
        super().__init__()
        self.previous_state = None
        try:
            rospy.init_node("omni_engine", anonymous=True)
        except rospy.exceptions.ROSException:
            pass

        self.type_mapping = {"robot": "VSWARM", "obstacle": "OBSTACLE", "prey": "PREY", 'leader': 'LEADER'}
        self.subscribers = []
        self.mqtt_client = self.start_up_mqtt_thread()
        self.joy_input = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.joy_timeout = 0.1
        self.last_joy_input_time = rospy.Time.now()
        self.control_id = 0
        self.is_locked = False  # 小车移动锁定状态
        self.led_enabled = False  # LED是否开启
        self.debug_mode = False  # 调试模式状态
        self.controlled_entity_ids = [eid for eid, e in self._entities.items()]
        self.current_control_index = 0  # 当前控制对象在控制列表中的下标
        self.current_controlled_entity_id = None
        self.color_mapping = {
            "red": 0xFF0000,
            "green": 0x00FF00,
            "blue": 0x0000FF,
            "yellow": 0xFFFF00,
            "purple": 0xFF00FF,
            "cyan": 0x00FFFF,
            "white": 0xFFFFFF,
            "black": 0x000000,
            "gray": 0xFF0000,
        }
        # 上一帧的按钮与轴状态，用于检测按下事件边沿
        self.last_buttons = []
        self.last_axes = []

        self.joy_subscriber = rospy.Subscriber("/joy", Joy, self.joy_callback)
        self.obs_subscriber = rospy.Subscriber("/observation", Observations, self.obs_callback)

    def start_up_mqtt_thread(self):
        broker_ip = "10.0.2.66"
        port = 1883
        keepalive = 60
        client_id = f"{self.__class__.__name__}"

        try:
            broker = os.environ["REMOTE_SERVER"]
        except KeyError:
            broker = broker_ip

        net_status = -1
        while net_status != 0:
            net_status = os.system(f"ping -c 4 {broker}")
            time.sleep(2)

        mqtt_client_instance = MqttClientThread(
            broker=broker, port=port, keepalive=keepalive, client_id=client_id
        )
        return mqtt_client_instance

    def obs_callback(self, msg: Observations):
        try:
            json_str = json_message_converter.convert_ros_message_to_json(msg)
            self.mqtt_client.publish("/observation", json_str.encode("utf-8"))
        except Exception as e:
            rospy.logerr(f"Error in obs_callback: {e}")

    def pose_callback(self, msg, args):
        entity_id, entity_type = args
        position = np.array([msg.pose.position.x, msg.pose.position.y])
        self.set_position(entity_id, position)
        # print(f"Entity {entity_id} position: {position}")
        quaternion = np.array(
            [
                msg.pose.orientation.x,
                msg.pose.orientation.y,
                msg.pose.orientation.z,
                msg.pose.orientation.w,
            ]
        )

        rot_mat = R.from_quat(quaternion).as_matrix()
        euler = np.array(R.from_matrix(rot_mat).as_euler("xyz", degrees=False))
        self.set_yaw(entity_id, euler[2])

    def twist_callback(self, msg, args):
        entity_id, entity_type = args
        velocity = np.array([msg.twist.linear.x, msg.twist.linear.y])
        entity_id = int(entity_id)
        self.set_velocity(entity_id, velocity)

    def joy_callback(self, joy_msg):
        # 检测按键上升沿
        if not self.last_buttons:
            self.last_buttons = joy_msg.buttons
        if not self.last_axes:
            self.last_axes = joy_msg.axes

        current_buttons = joy_msg.buttons
        current_axes = joy_msg.axes

        def button_pressed(btn_idx):
            return (current_buttons[btn_idx] == 1 and (
                    len(self.last_buttons) > btn_idx and self.last_buttons[btn_idx] == 0))

        # A 按键：切换锁定和解锁
        if button_pressed(0):  # A按钮
            self.is_locked = not self.is_locked
            msg = Bool(data=self.is_locked)
            json_str = json_message_converter.convert_ros_message_to_json(msg)
            self.mqtt_client.publish("/lock", json_str.encode("utf-8"))
        # B 按键：调整朝向
        if button_pressed(1):  # B按钮
            for entity_id, entity in self._entities.items():
                while True:
                    current_yaw = entity.yaw
                    yaw_error = 0 - current_yaw
                    if yaw_error > np.pi:
                        yaw_error -= 2 * np.pi
                    if yaw_error < -np.pi:
                        yaw_error += 2 * np.pi

                    if abs(yaw_error) < 0.1:
                        break
                    # 调用control_yaw使小车慢慢转正
                    self.control_yaw(entity_id, 0)
                    rospy.sleep(0.05)
        # X 按键：切换Debug模式
        if button_pressed(2):  # X按钮
            self.debug_mode = not self.debug_mode
        # Y 按键：切换LED显示
        if button_pressed(3):  # Y按钮
            self.led_enabled = not self.led_enabled

        def rt_pressed():
            return (self.last_axes and len(self.last_axes) > 5 and current_axes[5] < 0.5 and self.last_axes[5] > 0.5)

        if rt_pressed() and self.debug_mode:
            entity_ids = list(self._entities.keys())
            if entity_ids:
                self.current_control_index = (self.current_control_index + 1) % len(entity_ids)
                self.current_controlled_entity_id = entity_ids[self.current_control_index]

        # 使用手柄的轴控制小车速度（若未锁定则发送控制信号）
        # 左摇杆Y轴：axes[1], 左摇杆X轴：axes[0]
        # 右摇杆X轴：axes[3]控制转向
        self.joy_input["x"] = joy_msg.axes[1] * -0.25
        self.joy_input["y"] = joy_msg.axes[0] * -0.25
        self.joy_input["theta"] = joy_msg.axes[3] * 2
        self.last_joy_input_time = rospy.Time.now()

        self.last_buttons = current_buttons
        self.last_axes = current_axes

    def generate_subscribers(self, entity_id, entity_type):
        pose_topic = f"/vrpn_client_node/{entity_type.upper()}{entity_id}/pose"
        twist_topic = f"/vrpn_client_node/{entity_type.upper()}{entity_id}/twist"

        self.subscribers.append(
            rospy.Subscriber(
                pose_topic,
                PoseStamped,
                self.pose_callback,
                callback_args=(entity_id, entity_type),
            )
        )
        self.subscribers.append(
            rospy.Subscriber(
                twist_topic,
                TwistStamped,
                self.twist_callback,
                callback_args=(entity_id, entity_type),
            )
        )

    def generate_all_subscribers(self):
        for entity_id, entity in self._entities.items():
            a = entity.__class__.__name__.lower()
            self.generate_subscribers(
                entity_id=entity_id, entity_type=self.type_mapping[a]
            )

    def step(self, delta_time: float):
        current_state = {
            "led_enabled": self.led_enabled,
            "is_locked": self.is_locked,
            "debug_mode": self.debug_mode,
            "controlled_entity_id": self.current_controlled_entity_id
        }

        if len(self.subscribers) == 0:
            self.generate_all_subscribers()

        if not self.is_locked:
            self.apply_joy_control()

        if current_state != self.previous_state:
            if not self.debug_mode:
                self.update_led_color()
            else:
                self.set_all_led_off()
                if self.current_controlled_entity_id is not None:
                    self.set_entity_led_on(self.current_controlled_entity_id)
        self.previous_state = current_state

        rospy.sleep(delta_time)

    def apply_force(self, entity_id: int, force: np.ndarray):
        rospy.logwarn(f"Failed Applying force {force} to entity {entity_id} at omni bot")

    def control_velocity(self, entity_id, desired_velocity, dt=None):
        json_msg = {
            "x": desired_velocity["x"],
            "y": desired_velocity["y"],
            "theta": desired_velocity["theta"],
        }
        json_str = json.dumps(json_msg)
        self.mqtt_client.publish(
            f"/VSWARM{entity_id}_robot/motion", json_str.encode("utf-8")
        )

    def apply_joy_control(self):
        target_id = None
        if self.current_controlled_entity_id is not None and self.debug_mode:
            target_id = self.current_controlled_entity_id
        else:
            # 若无指定控制对象，则寻找一个prey, lead
            for entity_id, entity in self._entities.items():
                if entity.__class__.__name__.lower() == "prey":
                    target_id = entity_id
                    break
                if entity.__class__.__name__.lower() == "leader":
                    target_id = entity_id
                    break

        if target_id is not None:
            self.control_velocity(target_id, self.joy_input)

    def control_yaw(self, entity_id, desired_yaw, dt=None):
        current_yaw = self._entities[entity_id].yaw
        yaw_error = desired_yaw - current_yaw
        if yaw_error > np.pi:
            yaw_error -= 2 * np.pi
        if yaw_error < -np.pi:
            yaw_error += 2 * np.pi

        kp = 0.8
        angular_velocity = yaw_error * kp
        json_msg = {"x": 0, "y": 0, "theta": angular_velocity}
        json_str = json.dumps(json_msg)
        self.mqtt_client.publish(
            f"/VSWARM{entity_id}_robot/motion", json_str.encode("utf-8")
        )

    # ---------------------- Led ----------------------
    def set_all_led_off(self):
        for entity_id in self._entities:
            self.set_ledup(entity_id, 0x000000)
            self.set_leddown(entity_id, 0x000000)

    def set_entity_led_on(self, entity_id, color=None):
        if color is None:
            color = self.color_mapping[self._entities[entity_id].color]
        self.set_ledup(entity_id, color)
        self.set_leddown(entity_id, color)

    def update_led_color(self):

        if self.debug_mode:
            return

        try:
            for entity_id in self._entities:
                if self.led_enabled:
                    color = self.color_mapping.get(self._entities[entity_id].color, 0x000000)
                else:
                    color = self.color_mapping["black"]
                self.set_entity_led_on(entity_id, color)
        except KeyError as e:
            rospy.logerr("Color not found in color mapping")
            raise SyntaxError(e)

    def set_ledup(self, entity_id, led_colors):
        json_msg = {
            "cmd_type": "ledup",
            "args_length": 6,
            "args": {
                "0": led_colors,
                "1": 14,
                "2": led_colors,
                "3": 14,
                "4": led_colors,
                "5": 14,
            },
        }
        json_str = json.dumps(json_msg)
        self.mqtt_client.publish(
            f"/VSWARM{entity_id}_robot/cmd", json_str.encode("utf-8")
        )

    def set_leddown(self, entity_id, led_colors):
        json_msg = {
            "cmd_type": "leddown",
            "args_length": 6,
            "args": {
                "0": led_colors,
                "1": 30,
                "2": led_colors,
                "3": 30,
                "4": led_colors,
                "5": 30,
            },
        }
        json_str = json.dumps(json_msg)
        self.mqtt_client.publish(
            f"/VSWARM{entity_id}_robot/cmd", json_str.encode("utf-8")
        )
