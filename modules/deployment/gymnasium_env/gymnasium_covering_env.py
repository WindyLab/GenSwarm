from typing import Any, Optional, SupportsFloat, TypeVar

from modules.deployment.entity import Robot, Obstacle
from modules.deployment.utils.sample_point import *
from modules.deployment.gymnasium_env.gymnasium_base_env import GymnasiumEnvironmentBase


class GymnasiumCoveringEnvironment(GymnasiumEnvironmentBase):
    def __init__(self, data_file: str):
        super().__init__(data_file)

    def init_entities(self):
        entity_id = 0
        robot_size = self.data["entities"]["robot"]["size"]
        shape = self.data["entities"]["robot"]["shape"]
        color = self.data["entities"]["robot"]["color"]
        # obstacle_list = [(0, 0)]
        # for pos in obstacle_list:
        #     obstacle = Obstacle(entity_id, pos, 0.15)
        #     self.add_entity(obstacle)
        #     entity_id += 1
        for i in range(self.num_robots):
            position = sample_point(zone_center=[0, 0], zone_shape='rectangle',
                                    zone_size=[0.5 * self.width, 0.5 * self.height],
                                    robot_size=robot_size, robot_shape=shape, min_distance=0.1,
                                    entities=self.entities)
            robot = Robot(robot_id=entity_id,
                          initial_position=position,
                          target_position=None,
                          size=robot_size,
                          color=color)
            self.add_entity(robot)
            entity_id += 1


if __name__ == "__main__":

    import time
    import rospy

    from modules.deployment.utils.manager import Manager

    env = GymnasiumCoveringEnvironment("../../../config/env/clustering_config.json")

    obs, infos = env.reset()
    manager = Manager(env)
    manager.publish_observations(infos)
    rate = rospy.Rate(env.FPS)

    start_time = time.time()  # 记录起始时间
    frame_count = 0  # 初始化帧数计数器

    while time.time() - start_time < 60:
        action = manager.robotID_velocity
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
