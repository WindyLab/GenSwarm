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

from typing import Optional, TypeVar

from modules.deployment.engine import QuadTreeEngine, Box2DEngine, PyBullet2DEngine
from modules.deployment.entity import Robot, PushableObject, Landmark
from modules.deployment.utils.sample_point import *
from modules.deployment.gymnasium_env.gymnasium_base_env import GymnasiumEnvironmentBase

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")


class GymnasiumTransportationEnvironment(GymnasiumEnvironmentBase):
    def __init__(self, data_file: str):
        super().__init__(data_file)
        self.engine = QuadTreeEngine(
            world_size=(self.width, self.height),
            alpha=0.5,
            damping=0.75,
            collision_check=True,
            joint_constraint=True,
        )

    def init_entities(self):
        target_position = np.array((1, 2))
        zone_size = 1
        target_zone = Landmark(
            landmark_id=0,
            initial_position=target_position - zone_size * 0.5,
            size=np.array((zone_size, zone_size)),
            color="gray",
        )
        self.add_entity(target_zone)

        object = PushableObject(
            object_id=1, initial_position=(0, 0), size=0.3, color="red"
        )
        object.density = 0.1
        object.target_position = target_position
        self.add_entity(object)

        entity_id = 2
        robot_size = self.data["entities"]["robot"]["size"]
        shape = self.data["entities"]["robot"]["shape"]
        color = self.data["entities"]["robot"]["color"]

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


if __name__ == "__main__":
    import time
    import rospy

    from modules.deployment.utils.manager import Manager

    env = GymnasiumTransportationEnvironment(
        "../../../config/env/transportation_config.json"
    )

    obs, infos = env.reset()
    manager = Manager(env)
    manager.publish_observations(infos)
    rate = rospy.Rate(env.FPS)

    start_time = time.time()  # 记录起始时间
    frame_count = 0  # 初始化帧数计数器

    while True:
        action = manager.robotID_velocity
        # action = {}
        manager.clear_velocity()
        obs, reward, termination, truncation, infos = env.step(action=action)
        env.render()
        manager.publish_observations(infos)
        rate.sleep()

        frame_count += 1  # 增加帧数计数器
        current_time = time.time()  # 获取当前时间
        elapsed_time = current_time - start_time  # 计算已过去的时间

        # 当达到1秒时，计算并打印FPS，然后重置计数器和时间
        if elapsed_time >= 1.0:
            fps = frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")  # 打印FPS，保留两位小数
            frame_count = 0  # 重置帧数计数器
            start_time = current_time  # 重置起始时间戳
    print("Simulation completed successfully.")
