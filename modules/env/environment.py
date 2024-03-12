from os import listdir, makedirs

import matplotlib.pyplot as plt
import numpy as np
import rospy
from matplotlib.ticker import MultipleLocator
from std_srvs.srv import SetBool, SetBoolResponse
from manager import Manager


class Env:
    def __init__(
            self,
            size=(10, 10),
            n_robots=3,
            dt=0.1,
            if_leader=False,
            leader_speed=0.5,
            render_interval=1,
            magnification=1.1
    ):
        rospy.init_node('env_node', anonymous=True)
        self._size = size
        self._dt = dt
        self._render_interval = render_interval
        self._leader_speed = leader_speed
        self._manager = Manager(n_robots, size, if_leader=if_leader)
        self._robots = self._manager.robots
        rospy.set_param('robots_num', n_robots)

        # list of the robot color
        self._colors = plt.colormaps.get_cmap('viridis')(np.linspace(0, 1, n_robots))

        if if_leader:
            self._leader = self._robots.leader
            n_robots += 1
            red = np.array([[1.0, 0, 0, 1]], dtype=np.float64)  # Red in RGABs
            self._colors = np.append(self._colors, red, axis=0)
        else:
            self._leader = None
        self._robots_initial_positions = self._robots.positions.copy()
        self._reset_service = rospy.Service('/reset_environment', SetBool, self.reset_environment_callback)

        # flag to indicate if the test is running,if running, the robots will save their positions to history
        self._run_test = False
        # flag to indicate if the frames should be rendered
        self._render_frames = False
        self._fig, self._ax = plt.subplots()
        # path to save the frames
        self._data_path = rospy.get_param('data_path', '.')

        try:
            self._count = len(listdir(f"{self._data_path}/frames/"))  # # this is used to number the 'frames' folder
        except Exception as e:
            print("Exception: ", e)
        # counter for total run time
        self._run_time = 0

        # history of the robots' positions ,pop from the deque
        self._history = None

        # map magnification factor
        self._magn = magnification

    def reset_environment_callback(self, req):
        """
        reset_environment_callback is a callback function for the reset_environment service.
        It resets the environment to its initial state and returns a success message.
        must be called before and after running the script
        """
        self.reset()
        self._render_frames = req.data
        print("set render frames to", self._render_frames)

        response = SetBoolResponse()
        response.success = True
        response.message = "Environment reset successful!"
        return response

    def reset(self):
        """
        Reset the environment to its initial state.
        """
        self._run_test = not self._run_test
        if self._run_test:
            self._data_path = rospy.get_param('data_path', '.')
            print("Data path: ", self._data_path)
            self._robots.positions = self._robots_initial_positions.copy()
            self._robots.velocities = np.zeros_like(self._robots.velocities)
            self._robots.history = [self._robots.positions.copy()]
            try:
                self._count = len(listdir(f"{self._data_path}/frames/"))  # this is used to number the 'frames' folder
                makedirs(f"{self._data_path}/frames/frame{self._count}")
            except Exception as e:
                print("Exception: ", e)
            print(f"Test{self._count} started!\nSave images in {self._data_path}/frames/frame{self._count}")
        else:
            print(f"Test{self._count} stopped!\n")

    def step(self):
        if self._run_test:
            if self._leader:
                self._leader.move(self._leader_speed, self._dt)
            self._robots.move_robots(self._dt)
            self._run_time += 1
            self.render()

    def render(self):
        if not plt.get_fignums():
            self._fig, self._ax = plt.subplots()
        self._ax.clear()
        try:
            self._history = self._manager.robots.histories.pop()
        except IndexError:
            print("No more history to pop!")
        if self._history is None:
            return
        traj_len, robot_num, _ = self._history.shape
        for i in range(robot_num):
            show_len = min(20, traj_len)
            self._ax.plot(
                self._history[-show_len:, i, 0],
                self._history[-show_len:, i, 1],
                '.',  # use '.' can show the speed of the robots by the density of the trajectory points
                markersize=1,
                color=self._colors[i],
                label=f"Robot {i} path",
            )
            self._ax.plot(
                self._history[-1, i, 0],
                self._history[-1, i, 1],
                'o',
                markersize=5,
                color=self._colors[i],
                label=f"Robot {i} position",
            )
        if self._leader:
            self._ax.plot(
                self._leader.position[0],
                self._leader.position[1],
                marker='*',
                markersize=12,
                color=self._colors[-1],
                linestyle='None',
                label="Leader position"
            )

        major_locator = MultipleLocator(1)
        self._ax.xaxis.set_major_locator(major_locator)
        self._ax.yaxis.set_major_locator(major_locator)
        self._ax.set_xlim(-self._magn / 2 * self._size[0], self._magn / 2 * self._size[0])
        self._ax.set_ylim(-self._magn / 2 * self._size[1], self._magn / 2 * self._size[1])
        if self._render_frames:
            plt.draw()
            plt.pause(0.001)  # This is necessary for the plot to update
        frame_id = len(self._robots.history)
        plt.savefig(f'{self._data_path}/frames/frame{self._count}/{frame_id}.png')

    def run(self):
        print("Environment started!")
        rate = rospy.Rate(10 / self._dt)
        while not rospy.is_shutdown():
            self.step()
            rate.sleep()
        print("Environment stopped!")


if __name__ == "__main__":
    env = Env(if_leader=True, n_robots=10, size=(10, 10), leader_speed=-1)
    env.run()
