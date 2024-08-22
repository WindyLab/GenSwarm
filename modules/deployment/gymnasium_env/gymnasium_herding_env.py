from typing import Optional, TypeVar

from modules.deployment.entity import Robot, Sheep, Wall, Landmark
from modules.deployment.utils.sample_point import *
from modules.deployment.gymnasium_env.gymnasium_base_env import GymnasiumEnvironmentBase

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")


class GymnasiumHerdingEnvironment(GymnasiumEnvironmentBase):

    def __init__(self, data_file: str):
        super().__init__(data_file)

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed, options=options)
        self.entities = []
        self.init_entities()
        obs = self.get_observation("array")
        infos = self.get_observation("dict")
        return obs, infos

    def init_entities(self):
        entity_id = 0
        target_zone = Landmark(landmark_id=entity_id,
                               initial_position=(0, 0),
                               size=np.array((1, 1)),
                               color='gray', )
        self.add_entity(target_zone)
        entity_id += 1


        robot_size = self.data["entities"]["robot"]["size"]
        shape = self.data["entities"]["robot"]["shape"]
        color = self.data["entities"]["robot"]["color"]

        for i in range(self.num_robots):
            position = sample_point(zone_center=[0, 0], zone_shape='rectangle', zone_size=[self.width, self.height],
                                    robot_size=robot_size, robot_shape=shape, min_distance=0.5,
                                    entities=self.entities)
            dog = Robot(robot_id=entity_id,
                        initial_position=position,
                        size=robot_size,
                        color=color)
            self.add_entity(dog)
            entity_id += 1

        sheep_size = self.data.get("entities").get("sheep", {}).get("size", 0.15)
        shape = self.data.get("entities").get("sheep", {}).get("shape", "circle")
        color = self.data.get("entities").get("sheep", {}).get("color", "blue")

        for i in range(self.num_sheep):
            position = sample_point(zone_center=[0, 0], zone_shape='rectangle', zone_size=[self.width, self.height],
                                    robot_size=sheep_size, robot_shape=shape, min_distance=sheep_size,
                                    entities=self.entities)
            # position = [0,0]
            sheep = Sheep(prey_id=entity_id,
                          initial_position=position,
                          size=sheep_size)
            self.add_entity(sheep)
            entity_id += 1


    def step(self, action=ActType):
        obs, reward, termination, truncation, infos = super().step(action)

        for entity in self.entities:
            if isinstance(entity, Sheep):
                # 获取邻居羊群和机器人列表
                sheep = [e for e in self.entities if isinstance(e, Sheep) and e != entity]
                robots = [e for e in self.entities if isinstance(e, Robot)]
                speed = entity.calculate_velocity(sheep, robots,
                                                  environment_bounds=[-0.5 * self.width, 0.5 * self.width,
                                                                      -0.5 * self.height, 0.5 * self.height])
                self.set_entity_velocity(entity.id, speed)

        return obs, reward, termination, truncation, infos


if __name__ == "__main__":

    import time
    import rospy

    from modules.deployment.utils.manager import Manager

    env = GymnasiumHerdingEnvironment("../../../config/env_config.json")

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
