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
import rospy
from code_llm.msg import Observations
import os
from paho.mqtt import client as mqtt_client
from rospy_message_converter import json_message_converter
from modules.utils import rich_print


class MqttClientThread:
    def __init__(self, broker, port, keepalive, client_id):
        self.broker = broker  # MQTT代理服务器地址
        self.port = port
        self.keepalive = keepalive
        self.reconnect_interval = 1
        self.client_id = client_id
        self.client = self.connect_mqtt()
        self.client.loop_start()

    def connect_mqtt(self):
        """连接MQTT代理服务器"""

        def on_connect(client, userdata, flags, rc):
            """连接回调函数"""
            if rc == 0:
                rich_print(title="Connect to MQTT", content="Connected to MQTT OK!")
            else:
                rich_print(
                    title="Connect to MQTT",
                    content=f"Failed to connect, return code {rc}",
                )

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        try:
            client.connect(self.broker, self.port, self.keepalive)
        except Exception as e:
            rich_print(title="Connect to MQTT", content=f"Connection error: {e}")
        return client

    def publish(self, topic, msg):
        """发布消息到指定主题"""
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            pass
        else:
            print(f"Failed to send message to topic {topic}")

    def run(self):
        """启动MQTT客户端"""
        try:
            self.client.loop_forever()
        except Exception as e:
            print(f"Error in MQTT loop: {e}")
            time.sleep(self.reconnect_interval)
            try:
                self.client.loop_forever()
            except Exception as reconnect_error:
                print(f"Failed to reconnect: {reconnect_error}")
                # 再次等待一段时间后继续循环尝试
                time.sleep(self.reconnect_interval)
            # 继续循环，如果仍无法连接，继续捕获异常并处理


def obs_callback(client, msg: Observations):
    """ROS订阅消息回调函数"""
    try:
        json_str = json_message_converter.convert_ros_message_to_json(msg)
        client.publish("/observation", json_str.encode("utf-8"))
    except Exception as e:
        print(f"Error in obs_callback: {e}")


def main():
    broker_ip = "10.0.2.66"
    port = 1883
    keepalive = 60  # 与代理通信之间允许的最长时间段（以秒为单位）
    client_id = f"{socket.gethostname()}_robot_pub"  # 客户端id不能重复

    try:
        broker = os.environ["REMOTE_SERVER"]
    except KeyError:
        broker = broker_ip

    net_status = -1
    while net_status != 0:
        net_status = os.system(f"ping -c 4 {broker}")
        time.sleep(2)

    # 启动MQTT客户端线程
    mqtt_client_instance = MqttClientThread(
        broker=broker, port=port, keepalive=keepalive, client_id=client_id
    )
    mqtt_thread = threading.Thread(target=mqtt_client_instance.run)
    mqtt_thread.start()

    # 订阅ROS话题
    rospy.Subscriber(
        "/observation",
        Observations,
        lambda msg: obs_callback(mqtt_client_instance, msg),
    )

    ros_hz = 10
    rate = rospy.Rate(ros_hz)
    while not rospy.is_shutdown():
        try:
            rate.sleep()
        except rospy.ROSInterruptException:
            rospy.logerr("ROS Interrupt Exception! Just ignore the exception!")
        except rospy.ROSTimeMovedBackwardsException:
            rospy.logerr("ROS Time Backwards! Just ignore the exception!")


if __name__ == "__main__":
    rospy.init_node("mqtt_pub")

    main()
