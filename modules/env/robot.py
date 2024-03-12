import numpy as np
from collections import deque

import rospy
from geometry_msgs.msg import Twist


class Robot:
    def __init__(self, robot_id, initial_position, max_speed=2.0, communication_range=5.0):
        self._id = robot_id
        self._position = np.array(initial_position, dtype=float)
        self._velocity = np.array([0.0, 0.0], dtype=float)
        self._max_speed = max_speed
        self._communication_range = communication_range
        self._history = [self._position.copy()]

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, new_velocity):
        if np.linalg.norm(new_velocity) > self._max_speed:
            new_velocity = new_velocity / np.linalg.norm(new_velocity) * self._max_speed
        self._velocity = np.array(new_velocity, dtype=float)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = np.array(value, dtype=float)
        self._history.append(self._position)

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = value

    @property
    def id(self):
        return self._id

    @property
    def communication_range(self):
        return self._communication_range

    @property
    def max_speed(self):
        return self._max_speed


class Robots:
    def __init__(self, n_robots, env_size, if_leader=False):
        self._env_size = env_size
        initial_positions = self.generate_robots_random_positions(n_robots)
        self._robots = self.create_robots(n_robots, initial_positions)
        if if_leader:
            self._leader = Leader(initial_position=(0, 0))
            self._robots.append(self._leader)
        self._positions = np.array([robot.position for robot in self._robots])
        self._velocities = np.array([robot.velocity for robot in self._robots])
        self._history = [self._positions]
        self._histories = deque(maxlen=1000)

    @staticmethod
    def create_robots(n_robots, initial_positions):
        robots_list = []
        for i in range(n_robots):
            # id starts from 1
            robots_list.append(Robot(i + 1, initial_positions[i]))
        return robots_list

    def generate_robots_random_positions(self, n_robots):
        return [[np.random.uniform(-self._env_size[0] / 2, self._env_size[0] / 2),
                 np.random.uniform(-self._env_size[1] / 2, self._env_size[1] / 2)] for _ in range(n_robots)]

    @property
    def positions(self):
        self._positions = np.array([robot.position for robot in self._robots])
        return self._positions

    @property
    def robots(self):
        return self._robots

    @property
    def leader(self):
        return self._leader

    @positions.setter
    def positions(self, new_positions):
        assert new_positions.shape == self._positions.shape, f"Expected shape {self._positions.shape}, got {new_positions.shape}"
        self._positions = new_positions
        for i, robot in enumerate(self._robots):
            robot.position = new_positions[i]
        self._history.append(self._positions)

        self._histories.append(np.array(self._history))

    @property
    def velocities(self):
        self._velocities = np.array([robot.velocity for robot in self._robots])
        return self._velocities

    @velocities.setter
    def velocities(self, new_velocities):
        assert new_velocities.shape == self._velocities.shape, f"Expected shape {self._velocities.shape}, got {new_velocities.shape}"
        self._velocities = new_velocities
        for i, robot in enumerate(self._robots):
            robot.velocity = new_velocities[i]

    @property
    def history(self):
        return np.array(self._history)

    @property
    def histories(self):
        return self._histories

    @history.setter
    def history(self, value):
        self._history = value

    def move_robots(self, dt):
        """
        Move the robots according to their velocities.
        Args:
            dt: time step

        Returns: None

        """
        new_positions = self.positions + self.velocities * dt
        self.positions = np.clip(new_positions, -np.array(self._env_size) / 2, np.array(self._env_size) / 2)


class Leader(Robot):
    def __init__(self, initial_position, max_speed=2.0):
        super().__init__(robot_id=0, initial_position=initial_position, max_speed=max_speed)
        self.trajectory = []
        self.angle = 0
        self.position = initial_position
        self._subscriber = rospy.Subscriber('/leader/velocity', Twist, self.velocity_callback)

    def velocity_callback(self, data: Twist):
        self.velocity = np.array([data.linear.x, data.linear.y])
        self.velocity = np.clip(self.velocity, -self.max_speed, self.max_speed)

    def move_in_circle(self, center, radius, speed, dt):
        if abs(speed) > self.max_speed:
            speed = np.sign(speed) * self.max_speed

        # The way mathematical integration maybe diverges
        omega = speed / radius
        self.angle += omega * dt

        # target position
        new_x = center[0] + radius * np.cos(self.angle)
        new_y = center[1] + radius * np.sin(self.angle)
        target_pos = np.array([new_x, new_y], dtype=np.float64)
        # delta pos = target pos vector - current pos vector
        delta_pos = target_pos - self.position
        if np.linalg.norm(delta_pos) > abs(speed) * dt:
            delta_pos = delta_pos / np.linalg.norm(delta_pos) * abs(speed) * dt

        # next position = current pos + delta pos
        self.position += delta_pos
        self.trajectory.append(self.position)

    def move(self, speed, dt, shape: str = None):
        # TODO add more methods to move the leader in different patterns
        if shape == 'circle':
            self.move_in_circle(center=[0, 0], radius=3, speed=speed, dt=dt)
        if shape is None:
            self.position += self.velocity * dt
