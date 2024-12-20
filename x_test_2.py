import json
import os
import time

import rospy

from paho.mqtt import client as mqtt_client


class LedEngine:
    def __init__(self):
        self.mqtt_client = self.start_up_mqtt_thread()
        self.entity_id = 7

    def start_up_mqtt_thread(self):
        broker_ip = "10.0.2.66"
        port = 1883
        keepalive = 60  # 与代理通信之间允许的最长时间（秒）
        client_id = f"{self.__class__.__name__}"  # 客户端ID需要唯一

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

    def update_led_color(self, color="black"):
        color_mapping = {
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

        try:
            color = color_mapping[color]
            self.set_ledup(self.entity_id, color)
            self.set_leddown(self.entity_id, color)
            print(f"LED color updated to {color}")
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
                print("Connected to MQTT OK!")
            else:
                print(f"Failed to connect, return code {rc}")

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        try:
            client.connect(self.broker, self.port, self.keepalive)
        except Exception as e:
            print(f"Connection error: {e}")
        return client

    def publish(self, topic, msg):
        """发布消息到指定主题"""
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            pass
            # print(f"Sent `{msg}` to topic `{topic}`")
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


if __name__ == '__main__':
    frequency = 0.1
    led = LedEngine()
    led.update_led_color('black')
    time.sleep(1)
    led.update_led_color('yellow')
    time.sleep(1)
    led.update_led_color('black')
    time.sleep(1)
    led.update_led_color('yellow')
    time.sleep(1)
    led.update_led_color('black')
    time.sleep(1)
    led.update_led_color('yellow')
    time.sleep(1)
    # while True:
    #     led.update_led_color('yellow')
    #     time.sleep(1 / frequency)
    #     led.update_led_color('black')
