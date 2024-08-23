import json
from typing import Any, Optional, SupportsFloat, TypeVar
from math import isnan

import numpy as np
import pygame
import gymnasium
from gymnasium import spaces
from gymnasium.utils import seeding

from modules.deployment.engine import Box2DEngine, QuadTreeEngine, OmniEngine
from abc import ABC, abstractmethod

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")
RenderFrame = TypeVar("RenderFrame")

"""
This function converts coordinates in pymunk into pygame coordinates.

The coordinate system in pygame is:
         (0, 0) +-------+ (width, 0)      + ──── → x
                |       |                 │
                |       |                 │
   (0, -height) +-------+ (width, height) ↓ y

The coordinate system in ours system is:
(-width/2, -height/2)+-------+ (-width/2, height/2) +──── → y
                    |       |                       │
                      (0, 0)                        │
                    |       |                       ↓ x
(-width/2, height/2)+-------+ (width/2, height/2)
"""


class GymnasiumEnvironmentBase(gymnasium.Env, ABC):
    metadata = {
        'render.modes': ['human'],
        'fps': 30
    }

    def __init__(self, data_file: str):
        """
        Base class for environments.
        Args:
            data_file (str): The environment display info and entity info
        """
        self.data_file = data_file
        try:
            with open(self.data_file, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Data file not found: {self.data_file}") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error decoding JSON from the data file: {self.data_file}") from e

        self.dt = self.data.get('dt', 0.01)
        self.FPS = 10
        self.screen = None
        self.simulation_data = {}
        self.scale_factor = self.data['display']['scale_factor']
        self.width = self.data['display']['width']
        self.height = self.data['display']['height']

        self.entities = []

        engine_type = self.data.get('engine_type', 'QuadTreeEngine')
        if engine_type == 'QuadTreeEngine':
            self.engine = QuadTreeEngine(world_size=(self.width, self.height),
                                         alpha=0.5,
                                         damping=0.75,
                                         collision_check=False,
                                         joint_constraint=False)
        elif engine_type == 'Box2DEngine':
            self.engine = Box2DEngine()
        elif engine_type == 'Omni_Engine':
            self.engine = OmniEngine()
        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")

        self.moveable_agents = {}
        self.num_robots = self.data.get("entities", {}).get("robot", {}).get("count", 0)
        self.num_leaders = self.data.get("entities", {}).get("leader", {}).get("count", 0)
        self.num_obstacles = self.data.get("entities", {}).get("obstacle", {}).get("count", 0)
        self.num_sheep = self.data.get("entities", {}).get("sheep", {}).get("count", 0)
        self.num_pushable_object = self.data.get("entities", {}).get("pushable_object", {}).get("count", 0)

        self.get_spaces()

        # self.screen = pygame.Surface((self.width * self.scale_factor, self.height * self.scale_factor))

        self.render_mode = self.data.get('render_mode', 'human')

        self.output_file = self.data.get('output_file', 'output.json')
        self.clock = pygame.time.Clock()

    def _seed(self, seed=None):
        """
        Set the random seed for the environment to ensure reproducibility.

        This function initializes the environment's random number generator with
        a specified seed or a randomly generated seed if none is provided. By
        controlling the seed, you ensure that the random processes in the environment
        produce the same results across different runs, which is crucial for debugging
        and reproducible experiments.

        Args:
            seed (int, optional): The seed value to initialize the random number generator.
                                  If not provided, a random seed is generated.

        Returns:
            list: A list containing the seed value used for the random number generator.
                  This list always contains one element which is the seed used.

        Examples:
            >>> env = CustomEnv()
            >>> env._seed(42)  # Setting the seed to 42
            [42]

            >>> env._seed()  # Setting a random seed
            [123456789]  # Example of a randomly generated seed value
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def close(self):
        """
        Properly close the environment and clean up resources.

        This method ensures that if a Pygame screen is open, it is properly closed
        and Pygame is properly quit. It sets the screen attribute to None after quitting.

        Returns:
            None
       """
        if self.screen is not None:
            if pygame.get_init():  # Check if Pygame is initialized
                pygame.quit()
            self.screen = None

    def get_spaces(self):
        """
        Define and set the observation and action spaces for the environment.

        This method sets the `observation_space` and `action_space` attributes of the
        environment based on the number of robots.
        The observation space and action space are defined as continuous spaces using `gymnasium.spaces.Box`.

        Returns:
            None
        """

        # TODO: update obs_space
        obs_dim = 3
        obs_space = spaces.Box(
            low=np.float32(-np.sqrt(2)),
            high=np.float32(np.sqrt(2)),
            shape=(obs_dim,),
            dtype=np.float32,
        )

        act_space = spaces.Box(
            low=np.float32(-1.0),
            high=np.float32(1.0),
            shape=(2,),
            dtype=np.float32,
        )

        self.observation_space = [obs_space for _ in range(self.num_robots)]
        self.action_space = [act_space for _ in range(self.num_robots)]

    def get_observation(self, type: str = "dict"):
        """
        Retrieve observations of the entities in the environment.

        This method returns the observations of the entities (e.g., robots) in the environment.
        The observations can be returned in two formats based on the specified type:

        1. "dict" (default): Returns a dictionary where each key is an entity's ID and the value
           is another dictionary containing the entity's position, velocity, size, type, target position,
           and color. This format is useful for detailed information, often used in `infos`.

        2. "array": Returns a list of positions for all entities, where each element is the position
           of an entity. This format is useful for representing the observation space in a simplified
           manner.

        Args:
            type (str): The format of the observation. Can be "dict" or "array".
                        Default is "dict".

        Returns:
            dict or list: The observation of the entities. If `type` is "dict", returns a dictionary
                          with detailed information of each entity. If `type` is "array", returns a list
                          of positions of each entity.
        """
        if type == "dict":
            obs = {}
            for entity in self.entities:
                obs[entity.id] = {
                    "position": entity.position,
                    "velocity": entity.velocity,
                    "size": entity.size,
                    "type": entity.__class__.__name__,
                    "target_position": entity.target_position if hasattr(entity, "target_position") else None,
                    "color": entity.color
                }

        elif type == "array":
            obs = []
            for entity in self.entities:
                obs.append(entity.position)
        else:
            raise ValueError(f"Unsupported observation type: {type}")

        return obs

    def step(
            self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        """
        Perform one step of the environment using the given actions.

        This method takes the actions for the current step, updates the environment state,
        and returns the observation, reward, termination status, truncation status, and additional info.

        Args:
            action (ActType): A dictionary where keys are entity IDs and values are the velocities
                              to be set for each entity. The specific structure of ActType should
                              be defined based on the environment's requirements.

        Returns:
            tuple:
                ObsType: The observation after performing the step, formatted as an array of positions.
                SupportsFloat: The reward obtained after performing the step.
                bool: A boolean indicating whether the episode has terminated.
                bool: A boolean indicating whether the episode has been truncated.
                dict[str, Any]: Additional information about the environment, formatted as a dictionary
                                with detailed information for each entity.
        """
        for entity_id, velocity in action.items():
            valid_velocity = [i if not isnan(i) else 0 for i in velocity]
            self.set_entity_velocity(entity_id, velocity)

        self.engine.step(self.dt)
        obs = self.get_observation("array")
        reward = self.reward()
        termination = False
        truncation = False
        infos = self.get_observation("dict")
        return obs, reward, termination, truncation, infos

    def reward(self):
        reward = {}
        for entity in self.entities:
            reward[entity.id] = 0
        return reward

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        self.draw()

        rgb_array = pygame.surfarray.pixels3d(self.screen)
        new_rgb_array = np.copy(rgb_array)
        del rgb_array

        if self.render_mode == "human":
            pygame.event.pump()
            pygame.display.update()
        return np.transpose(new_rgb_array, axes=(1, 0, 2))

    def draw(self):
        def apply_offset(pos):
            return pos[0] + self.width / 2, pos[1] + self.height / 2

        self.screen.fill((255, 255, 255))

        for entity in self.entities:
            pixel_pos = [int(i * self.scale_factor) for i in apply_offset(entity.position)]
            color = pygame.Color(entity.color)
            if entity.shape == 'circle':
                pygame.draw.circle(self.screen, color, [pixel_pos[1], pixel_pos[0]],
                                   int(entity.size * self.scale_factor))
            else:
                rect = pygame.Rect(
                    (pixel_pos[1] - entity.size[1] / 2 * self.scale_factor),
                    (pixel_pos[0] - entity.size[0] / 2 * self.scale_factor),
                    entity.size[1] * self.scale_factor,
                    entity.size[0] * self.scale_factor,
                )
                pygame.draw.rect(self.screen, color, rect)

    def reset(
            self,
            *,
            seed: int | None = None,
            options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        super().reset(seed=seed)
        self.entities = []
        self.engine.clear_entities()
        self.init_entities()
        obs = self.get_observation("array")
        infos = self.get_observation("dict")
        if self.render_mode == 'human':
            self.screen = pygame.display.set_mode((self.width * self.scale_factor, self.height * self.scale_factor))
        else:
            self.screen = pygame.Surface((self.width * self.scale_factor, self.height * self.scale_factor))

        return obs, infos

    @abstractmethod
    def init_entities(self):
        raise NotImplementedError(f"{str(self)}.init_entities method must be implemented.")

    def add_entity(self, entity):
        self.entities.append(entity)
        if entity.collision:
            self.engine.add_entity(entity)
        if entity.moveable:
            self.moveable_agents[entity.id] = entity.__class__.__name__

    def remove_entity(self, entity_id):

        self.entities = [entity for entity in self.entities if entity.id != entity_id]

        if self.entities[entity_id].collision:
            self.engine.remove_entity(entity_id)

    def get_entities_by_type(self, entity_type):
        """Get a list of entities of a specified type."""
        return [entity for entity in self.entities if entity.__class__.__name__ == entity_type]

    def get_entity_position(self, entity_id):
        """Get the position of the entity with the specified ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                entity.position = self.engine.get_entity_state(entity_id)[0]
                return entity.position
        raise ValueError(f"No entity with ID {entity_id} found.")

    def get_entity_velocity(self, entity_id):
        """Get the velocity of the entity with the specified ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                entity.velocity = self.engine.get_entity_state(entity_id)[1]
                return entity.velocity
        raise ValueError(f"No entity with ID {entity_id} found.")

    def set_entity_velocity(self, entity_id, velocity):
        """Set the velocity of the entity with the specified ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                self.engine.control_velocity(entity_id, velocity, self.dt)
                return
        raise ValueError(f"No entity with ID {entity_id} found.")

    def get_entity_by_id(self, entity_id):
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        raise ValueError(f"No entity with ID {entity_id} found.")

    def connect_to(self, entity1_id, entity2_id):
        entity1 = self.get_entity_by_id(entity1_id)
        entity2 = self.get_entity_by_id(entity2_id)
        distance = np.linalg.norm(entity1.position - entity2.position)
        if distance > 1.1 * (entity1.size + entity2.size):
            return False
        self.engine.add_joint(entity1_id, entity2_id, entity1.size + entity2.size)
        return True

    def disconnect_entities(self, entity1_id, entity2_id):
        try:
            entity1 = self.get_entity_by_id(entity1_id)
            entity2 = self.get_entity_by_id(entity2_id)
        except ValueError:
            return False
        self.engine.remove_joint(entity1_id, entity2_id)
        return True


if __name__ == '__main__':
    env = GymnasiumEnvironmentBase("../../../config/env_config.json")
