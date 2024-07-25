import json

import numpy as np
import pygame

from modules.deployment.entity.base_entity import Entity
from modules.deployment.entity.leader import Leader
from modules.deployment.entity.pushable_object import PushableObject
from modules.deployment.env import EnvironmentBase


class ClassificationEnvironment(EnvironmentBase):
    def __init__(self,
                 width: int,
                 height: int,
                 radius: int,
                 robot_num: int,
                 obstacle_num: int,
                 center: tuple = (500, 500),
                 output_file: str = "output.json"):
        super().__init__(width, height)
        self.radius = radius
        self.center = center
        self.output_file = output_file
        self.robot_num = robot_num
        self.obstacle_num = obstacle_num
        self.init_entities()

    def init_entities(self):

        obstacle_points = self.sample_points_inside_circle(self.radius, self.center, self.obstacle_num, 50)
        for entity_id, initial_position in enumerate(obstacle_points, start=0):
            object = PushableObject(object_id=entity_id,
                                    initial_position=initial_position,
                                    size=20.0,
                                    color='red')
            self.add_entity(object)

        leader = Leader(leader_id=0, initial_position=(0, 0), size=10.0)
        self.add_entity(leader)

    @staticmethod
    def find_farthest_points(points):
        points = np.array(points)
        distances = np.linalg.norm(points[:, np.newaxis] - points, axis=2)
        farthest_indices = np.argmax(distances, axis=1)
        return points[farthest_indices]

    @staticmethod
    def sample_points_on_circle(radius, center, num_points):
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = [(center[0] + radius * np.cos(angle),
                   center[1] + radius * np.sin(angle)) for angle in angles]
        return points

    @staticmethod
    def sample_points_inside_circle(radius, center, num_points, min_distance, max_attempts_per_point=10):
        def distance(p1, p2):
            return np.sqrt(np.sum((p1 - p2) ** 2, axis=1))

        points = []
        center = np.array(center)
        attempts = 0

        radius -= min_distance
        while len(points) < num_points and attempts < num_points * max_attempts_per_point:
            # Generate random points within the bounding square
            random_points = np.random.uniform(-radius, radius, size=(num_points, 2)) + center
            valid_mask = np.linalg.norm(random_points - center, axis=1) <= radius
            random_points = random_points[valid_mask]

            for point in random_points:
                if len(points) == 0 or np.all(distance(np.array(points), point) >= min_distance):
                    points.append(point)
                    if len(points) >= num_points:
                        break

            attempts += 1

        if len(points) < num_points:
            print(f"Warning: Could only place {len(points)} points out of {num_points} requested.")

        return np.array(points)
