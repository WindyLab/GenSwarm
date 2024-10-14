#!/usr/bin/python3
import rospy
import numpy as np
from geometry_msgs.msg import Twist


class VelocityLimiterNode:
    def __init__(self):
        rospy.init_node('velocity_limiter_node', anonymous=True)

        # Parameters from roslaunch or default values
        self.max_linear_speed = rospy.get_param('~max_linear_speed', 0.2)  # Default max linear speed
        self.publish_rate = rospy.get_param('~publish_rate', 10.0)  # Publish rate in Hz
        self.damping_factor = rospy.get_param('~damping_factor', 0.5)  # Damping factor (0 < factor < 1)
        self.time = rospy.get_param('~time', 200.0)

        self.vel_cmd_pub = rospy.Publisher('/robot/velcmd', Twist, queue_size=10)
        self.cmd_vel_sub = rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)

        self.timer = rospy.Timer(rospy.Duration(self.time), self.timer_callback)
        self.rate = rospy.Rate(self.publish_rate)

        # Store the last commanded velocity to apply damping
        self.last_linear_vel = np.zeros(3)
        self.last_angular_vel = np.zeros(3)

        rospy.spin()

    def cmd_vel_callback(self, msg):
        # Convert Twist message to numpy array
        linear_vel = np.array([msg.linear.x, msg.linear.y, msg.linear.z])
        angular_vel = np.array([msg.angular.x, msg.angular.y, msg.angular.z])

        # Apply damping to the velocities
        linear_vel = self.damping_factor * self.last_linear_vel + (1 - self.damping_factor) * linear_vel
        angular_vel = self.damping_factor * self.last_angular_vel + (1 - self.damping_factor) * angular_vel

        # Normalize linear velocity
        linear_norm = np.linalg.norm(linear_vel)
        if linear_norm > 0:
            linear_vel = linear_vel / linear_norm * min(linear_norm, self.max_linear_speed)

        # Update Twist message with normalized and damped velocities
        msg.linear.x, msg.linear.y, msg.linear.z = linear_vel
        msg.angular.x, msg.angular.y, msg.angular.z = angular_vel

        # Publish limited and damped velocity command
        self.vel_cmd_pub.publish(msg)

        # Store the current velocities as the last velocities
        self.last_linear_vel = linear_vel
        self.last_angular_vel = angular_vel

    def timer_callback(self, event):
        rospy.loginfo(f"Closing node after {self.time} seconds timeout.")
        rospy.signal_shutdown("Timeout reached.")


if __name__ == '__main__':
    try:
        VelocityLimiterNode()
    except rospy.ROSInterruptException:
        pass
