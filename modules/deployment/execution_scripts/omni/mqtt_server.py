#!/usr/bin/python3
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
import socket
import threading
import time

import numpy as np
import rospy
from code_llm.msg import Observations
import os
from std_msgs.msg import Bool

from geometry_msgs.msg import Twist
from paho.mqtt import client as mqtt_client
from rospy_message_converter import json_message_converter


class MqttClientThread:
    def __init__(self, broker, port, keepalive, client_id, hostname):
        self.broker = broker  # MQTT代理服务器地址
        self.port = port
        self.keepalive = keepalive
        self.hostname = hostname
        self.client_id = client_id
        self.stop_event = threading.Event()
        self.client = self.connect_mqtt()
        self.client.on_message = self.mqtt_callback
        self.client.subscribe("/observation")
        self.client.subscribe("/" + self.hostname + "_robot/motion")
        self.client.subscribe("/lock")
        rospy.init_node("mqtt_server")
        self.observation_pub = rospy.Publisher(
            "/observation", Observations, queue_size=1
        )

        self.vel_pub = rospy.Publisher("robot/velcmd", Twist, queue_size=10)
        self.lock_pub = rospy.Publisher("/lock", Bool, queue_size=1)

    def connect_mqtt(self):
        """连接MQTT代理服务器"""

        def on_connect(client, userdata, flags, rc):
            """连接回调函数"""
            if rc == 0:
                print("Connected to MQTT OK!")
            else:
                print(f"Failed to connect, return code {rc}")

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port, self.keepalive)
        return client

    def mqtt_callback(self, client, userdata, msg):
        """订阅消息回调函数"""
        if msg.topic == "/observation":
            obs_msg = msg.payload.decode()
            message = json_message_converter.convert_json_to_ros_message(
                "code_llm/Observations", obs_msg
            )
            self.observation_pub.publish(message)
        # elif msg.topic == ("/" + self.hostname + "_robot/motion"):
        #     vel_msg = msg.payload.decode()
        #     vel_msg = json_message_converter.convert_json_to_ros_message(
        #         "geometry_msgs/Twist", vel_msg
        #     )
        #     self.vel_pub.publish(vel_msg)
        elif msg.topic == "/lock":
            lock_msg = msg.payload.decode()
            lock_msg = json_message_converter.convert_json_to_ros_message(
                "std_msgs/Bool", lock_msg
            )
            self.lock_pub.publish(lock_msg)
        else:
            print(f"Unknown topic {msg.topic}")

    def run(self):
        while not self.stop_event.is_set():
            self.client.loop(timeout=1.0)

    def stop(self):
        self.stop_event.set()


def main():
    broker_ip = "10.0.2.66"
    port = 1883
    keepalive = 60  # 与代理通信之间允许的最长时间段（以秒为单位）
    hostname = socket.gethostname()
    client_id = f"{hostname}_robot_sub"  # 客户端ID不能重复

    try:
        broker = os.environ["REMOTE_SERVER"]
    except KeyError:
        broker = broker_ip

    while os.system(f"ping -c 4 {broker}") != 0:
        time.sleep(2)

    # 启动MQTT客户端线程
    mqtt_client_instance = MqttClientThread(
        broker=broker,
        port=port,
        keepalive=keepalive,
        client_id=client_id,
        hostname=hostname,
    )
    mqtt_thread = threading.Thread(target=mqtt_client_instance.run)
    mqtt_thread.start()

    ros_hz = 100
    rate = rospy.Rate(ros_hz)

    try:
        while not rospy.is_shutdown():
            rate.sleep()
    except rospy.ROSInterruptException:
        rospy.logerr("ROS Interrupt Exception! Just ignore the exception!")
    except rospy.ROSTimeMovedBackwardsException:
        rospy.logerr("ROS Time Backwards! Just ignore the exception!")
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping...")
    finally:
        mqtt_client_instance.stop()
        mqtt_thread.join()
        print("MQTT client thread stopped.")


if __name__ == "__main__":
    main()
