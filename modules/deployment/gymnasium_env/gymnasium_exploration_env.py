from typing import Optional, TypeVar

from modules.deployment.entity import Landmark, Robot
from modules.deployment.utils.sample_point import *
from modules.deployment.gymnasium_env.gymnasium_base_env import GymnasiumEnvironmentBase

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")
RenderFrame = TypeVar("RenderFrame")


class GymnasiumExplorationEnvironment(GymnasiumEnvironmentBase):
    def __init__(self, data_file: str):
        super().__init__(data_file)

    def init_entities(self):
        entity_id = 0
        for x in np.arange(-self.width * 0.45, self.width * 0.5, 0.1 * self.width):
            for y in np.arange(-self.height * 0.45, self.height * 0.5, 0.1 * self.height):
                landmark = Landmark(landmark_id=entity_id,
                                    initial_position=(x, y),
                                    size=np.array([0.1 * self.width, 0.1 * self.height]),
                                    color='gray')
                self.add_entity(landmark)
                entity_id += 1

        robot_size = self.data["entities"]["robot"]["size"]
        shape = self.data["entities"]["robot"]["shape"]
        color = self.data["entities"]["robot"]["color"]

        for i in range(self.num_robots):
            position = sample_point(zone_center=[0, 0], zone_shape='rectangle', zone_size=[0.1, 0.1],
                                    robot_size=robot_size, robot_shape=shape, min_distance=robot_size,
                                    entities=self.entities)
            robot = Robot(robot_id=entity_id,
                          initial_position=position,
                          target_position=None,
                          size=robot_size,
                          color=color)
            entity_id += 1
            self.add_entity(robot)

    def step(self, action: ActType):
        obs, reward, termination, truncation, infos = super().step(action)

        for entity in self.entities:
            if isinstance(entity, Robot):
                for landmark in self.entities:
                    if isinstance(landmark, Landmark):
                        if self.is_robot_within_landmark(entity, landmark):
                            landmark.color = 'blue'

        return obs, reward, termination, truncation, infos

    def is_robot_within_landmark(self, robot: Robot, landmark: Landmark):
        distance = np.linalg.norm(robot.position - landmark.position)
        landmark_radius = np.linalg.norm(landmark.size) / 2  # Assuming size is the diameter
        return distance <= landmark_radius


if __name__ == "__main__":

    import time
    import rospy

    from modules.deployment.utils.manager import Manager

    env = GymnasiumExplorationEnvironment("../../../config/env_config.json")

    obs, infos = env.reset()
    manager = Manager(env)
    manager.publish_observations(infos)
    rate = rospy.Rate(env.FPS)

    start_time = time.time()  # 记录起始时间
    frame_count = 0  # 初始化帧数计数器

    while True:
        # action = manager.robotID_velocity
        action = {}
        # manager.clear_velocity()
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
