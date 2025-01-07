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

import os
import sys
from typing import Optional, TypeVar

from modules.deployment.entity import Robot, Obstacle, Prey
from modules.deployment.utils.sample_point import *
from modules.deployment.gymnasium_env.gymnasium_base_env import GymnasiumEnvironmentBase
from modules.deployment.utils.save import save_frames_as_animations

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")
RenderFrame = TypeVar("RenderFrame")


class GymnasiumEncirclingEnvironment(GymnasiumEnvironmentBase):
    def __init__(self, data_file: str):
        super().__init__(data_file)

    def init_entities(self):
        entity_id = 0
        robot_size = self.data["entities"]["robot"]["size"]
        shape = self.data["entities"]["robot"]["shape"]
        color = self.data["entities"]["robot"]["color"]

        obstacle_list = [(0, 1.5), (0, -1.5), (0.8, 0), (-0.8, 0)]
        for pos in obstacle_list:
            obstacle = Obstacle(entity_id, pos, 0.15)
            self.add_entity(obstacle)
            entity_id += 1

        for i in range(self.num_robots):
            position = sample_point(
                zone_center=[0, 0],
                zone_shape="rectangle",
                zone_size=[self.width, self.height],
                robot_size=robot_size,
                robot_shape=shape,
                min_distance=robot_size,
                entities=self.entities,
            )
            robot = Robot(
                robot_id=entity_id,
                initial_position=position,
                target_position=None,
                size=robot_size,
                color=color,
            )
            self.add_entity(robot)
            entity_id += 1

        # obstacle_size = self.data["entities"]["obstacle"]["size"]
        # shape = self.data["entities"]["obstacle"]["shape"]
        # color = self.data["entities"]["obstacle"]["color"]
        #
        # for i in range(self.num_obstacles):
        #     position = sample_point(zone_center=[0, 0], zone_shape='rectangle', zone_size=[self.width, self.height],
        #                             robot_size=obstacle_size, robot_shape=shape, min_distance=obstacle_size,
        #                             entities=self.entities)
        #     obstacle = Obstacle(obstacle_id=entity_id,
        #                         initial_position=position,
        #                         size=obstacle_size)
        #     self.add_entity(obstacle)
        #     entity_id += 1

        prey_size = 0.1
        prey = Prey(
            prey_id=entity_id, initial_position=[0, 0], size=prey_size, num=2000
        )
        self.add_entity(prey)


if __name__ == "__main__":
    import time
    import rospy

    from modules.deployment.utils.manager import Manager
    from run.auto_runner.core import EnvironmentManager

    env = GymnasiumEncirclingEnvironment("../../../config/real_env/encircling_config.json")
    env_manager = EnvironmentManager(env)
    env_manager.start_environment(experiment_path=".", render_mode='human')

    rospy.spin()