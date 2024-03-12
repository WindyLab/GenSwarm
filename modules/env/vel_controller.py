import numpy as np
import rospy
from geometry_msgs.msg import Twist
from pynput.keyboard import Key, Listener


class SpeedController:
    def __init__(self, topic_name_pub: str, topic_name_sub: str = None, init_speed: float = 0.5):
        self._pub = rospy.Publisher(topic_name_pub, Twist, queue_size=1)
        self._twist = Twist()
        self._speed = init_speed
        if topic_name_sub:
            self._subscriber = rospy.Subscriber(topic_name_sub, Twist, self.callback)

    def callback(self, data):
        self._twist = data

    def publish(self):
        self._pub.publish(self._twist)


class KeyboardController(SpeedController):
    def __init__(self, topic_name_pub: str, topic_name_sub: str = None, init_speed: float = 0.5):
        super().__init__(topic_name_pub, topic_name_sub, init_speed)
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
        self._direction_map = {
            'w': (0, 1),
            'a': (-1, 0),
            's': (0, -1),
            'd': (1, 0)
        }
        self._direction = np.array([0, 0])

    def on_press(self, key):
        try:
            key_char = key.char
            print(f"Key pressed: {key_char}")
            if key_char in ['w', 'a', 's', 'd']:
                self._direction = np.array(self._direction_map[key_char])
        except AttributeError:
            if key == Key.up:
                self._speed += 0.1
            elif key == Key.down:
                self._speed -= 0.1
            elif key == Key.esc:
                self.listener.stop()
                rospy.signal_shutdown("Keyboard interrupt")
            elif key == Key.space:
                self._speed = 0

        speed = self._direction * self._speed
        print(f"Speed: {speed}")
        self._twist.linear.x = speed[0]
        self._twist.linear.y = speed[1]
        self.publish()


class GamepadController(SpeedController):
    def __init__(self, topic_name_pub: str, topic_name_sub: str = None, init_speed: float = 0.5):
        super().__init__(topic_name_pub, topic_name_sub, init_speed)


if __name__ == '__main__':
    rospy.init_node('controller_node', anonymous=True)
    controller = KeyboardController('/leader/velocity', )
    rospy.spin()
