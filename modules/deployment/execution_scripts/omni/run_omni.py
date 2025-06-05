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
import datetime
import os
import pickle

import signal
import sys
import threading
import rospy
import socket
import re

from local_skill import initialize_ros_node, run_loop


class RobotRunner:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.stop_event = threading.Event()

    def run(self, task=None):
        print(f"run code success with id={self.robot_id}")
        initialize_ros_node(
            robot_id=self.robot_id,
            assigned_task=task,
        )


        while not self.stop_event.is_set():
            run_loop()

    def stop(self):
        self.stop_event.set()


def run_robot_in_thread(robot_id):
    assigned = False
    robot_runner = RobotRunner(robot_id)
    try:
        with open(os.path.join("/catkin_ws/src/code_llm/allocate_result.pkl"), "rb") as f:
            task = pickle.load(f)
            print(f"Loaded tasks: {task}")
            assigned = True
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        print(f"Error loading file: {e}. Initializing a default task.")
    assigned_task = task[robot_id] if assigned else None
    print(f"Task assigned: {task[robot_id]}")

    robot_thread = threading.Thread(target=robot_runner.run, args=(assigned_task,))
    robot_thread.start()
    return robot_runner, robot_thread


def signal_handler(signum, frame, robot_runner):
    print("Signal handler called with signal", signum)
    robot_runner.stop()

    sys.exit(0)


if __name__ == "__main__":
    numbers = re.findall(r"\d+", socket.gethostname())
    numbers = list(map(int, numbers))

    if len(numbers) > 1:
        raise SystemExit(f"hostname:{socket.gethostname()},get numbers:{numbers}")

    robot_id = numbers[0]
    # robot_id = 1
    rospy.init_node(f"run_omni", anonymous=True)

    robot_runner, robot_thread = run_robot_in_thread(robot_id)

    signal.signal(
        signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, robot_runner)
    )

    try:
        robot_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        robot_runner.stop()
        robot_thread.join()
