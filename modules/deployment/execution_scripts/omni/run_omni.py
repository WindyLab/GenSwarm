#!/usr/bin/python3

import signal
import sys
import threading
import rospy
import socket
import re

from functions import initialize_ros_node, run_loop


class RobotRunner:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.stop_event = threading.Event()

    def run(self):
        print(f'run code success with id={self.robot_id}')
        initialize_ros_node(robot_id=self.robot_id)
        while not self.stop_event.is_set():
            run_loop()

    def stop(self):
        self.stop_event.set()


def run_robot_in_thread(robot_id):
    robot_runner = RobotRunner(robot_id)
    robot_thread = threading.Thread(target=robot_runner.run)
    robot_thread.start()
    return robot_runner, robot_thread


def signal_handler(signum, frame, robot_runner):
    print("Signal handler called with signal", signum)
    robot_runner.stop()
    sys.exit(0)


if __name__ == "__main__":
    numbers = re.findall(r'\d+', socket.gethostname())
    numbers = list(map(int, numbers))

    if len(numbers) > 1:
        raise SystemExit(f"hostname:{socket.gethostname()},get numbers:{numbers}")

    robot_id = numbers[0]
    # robot_id = 1
    rospy.init_node(f'run_omni', anonymous=True)

    robot_runner, robot_thread = run_robot_in_thread(robot_id)

    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, robot_runner))

    try:
        robot_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        robot_runner.stop()
        robot_thread.join()
