import geometry_msgs.msg
import numpy as np
import rospy
from geometry_msgs.msg import Point, Vector3, Twist
from code_llm.msg import Observations, ObjInfo
from robot import Robots
from obstacle import Obstacles


class Manager:
    def __init__(self, n_robots, n_obstacles, size, mode, if_leader=False, ):
        self._robots = Robots(n_robots, size, mode, if_leader=if_leader)
        self._obstacles = Obstacles(n_obstacles, size, robot_list=self._robots.robots)
        self._agent_num = n_robots
        self._if_leader = if_leader
        self._pub_list = []
        for i in range(self._agent_num):
            self._pub_list.append(
                rospy.Publisher(f"/robot_{i}/observation", Observations, queue_size=1)
            )
            rospy.Subscriber(
                f"/robot_{i}/velocity", Twist, self.velocity_callback, callback_args=i
            )

        self._timer = rospy.Timer(rospy.Duration(0.01), self.distribute)

    @property
    def robots(self) -> Robots:
        return self._robots

    @property
    def obstacles(self) -> Obstacles:
        return self._obstacles

    def velocity_callback(self, data: geometry_msgs.msg.Twist, i):
        """
        velocity_callback is a callback function for the velocity topic.
        """
        self._robots.robots[i].velocity = np.array([data.linear.x, data.linear.y])

    def distribute(self, event):
        """
        distribute is responsible for distributing the observations to the robots.
        """
        for i, robot in enumerate(self._robots.robots[0: self._agent_num]):
            observations_msg = Observations()
            observations_msg.observations = []
            for j, obj_j in enumerate(self._robots.robots + self._obstacles.obstacles):
                if j == i:
                    obj_type = "self"
                elif j < self._agent_num:
                    obj_type = "robot"
                elif j == self._agent_num:
                    obj_type = "leader" if self._if_leader else "obstacle"
                else:
                    obj_type = "obstacle"

                if (
                        np.linalg.norm(robot.position - obj_j.position)
                        <= robot.communication_range
                ):
                    liner_speed = (
                        Vector3(x=obj_j.velocity[0], y=obj_j.velocity[1], z=0)
                        if obj_type != "obstacle"
                        else Vector3(x=0, y=0, z=0)
                    )
                    observations_msg.observations.append(
                        ObjInfo(
                            id=obj_j.id,
                            type=obj_type,
                            position=Point(
                                x=obj_j.position[0], y=obj_j.position[1], z=0
                            ),
                            velocity=Twist(
                                linear=liner_speed, angular=Vector3(x=0, y=0, z=0)
                            ),
                            radius=obj_j.radius,
                        )
                    )

            self._pub_list[i].publish(observations_msg)
