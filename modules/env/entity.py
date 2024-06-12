import numpy as np
from typing import Union, List


class Entity:
    # TODO: 改成gym的标准接口
    # TODO: 使用向量来大规模计算
    def __init__(self,
                 entity_id: int,
                 initial_position: Union[List[float], tuple, np.ndarray],
                 size: Union[List[float], tuple, np.ndarray, float],
                 color: str,
                 collision: bool = False,
                 moveable: bool = False):
        """
        Initialize a new entity with the given parameters.
        Connectors means the entity is connected to another entity.

        :param entity_id: Unique identifier for the entity.
        :param initial_position: Initial position of the entity.
        :param size: Size of the entity.
        :param color: Color of the entity.
        :param collision: Indicates if the entity has collision enabled.
        :param moveable: Indicates if the entity is moveable.
        """
        self.__id = entity_id
        self.__position = np.array(initial_position, dtype=float)
        self.__history = [self.__position.copy()]
        self.__size = size
        self.__mass = 1.0
        self.__connector: List[Entity] = []
        self.__color: str = color
        self.__alpha: float = 0.7
        self.__collision: bool = collision
        self.__moveable: bool = moveable
        self.__velocity = np.array([0.0, 0.0], dtype=float)
        self.__max_speed = 2.0
        self.__shape = 'circle' if isinstance(size, float) else 'rectangle'

    @property
    def position(self) -> np.ndarray:
        """Get the current position of the entity."""
        return self.__position

    @position.setter
    def position(self, value: Union[List[float], tuple, np.ndarray]):
        """Set a new position for the entity."""
        if self.__moveable:
            self.__position = np.array(value, dtype=float)
            self.__history.append(self.__position.copy())
        else:
            raise ValueError("Entity is not moveable.")

    @property
    def history(self):
        """Get the historical positions of the entity."""
        return np.array(self.__history)

    @property
    def size(self) -> Union[List[float], tuple, np.ndarray, float]:
        """Get the size of the entity."""
        return self.__size

    @property
    def id(self) -> int:
        """Get the unique identifier of the entity."""
        return self.__id

    @property
    def color(self) -> str:
        """Get the color of the entity."""
        return self.__color

    @property
    def shape(self) -> str:
        """Get the shape of the entity."""
        return self.__shape

    @color.setter
    def color(self, value: str):
        """Set a new color for the entity."""
        if isinstance(value, str):
            self.__color = value
        else:
            raise ValueError("Color must be a string.")

    @property
    def alpha(self) -> float:
        """Get the transparency level of the entity."""
        return self.__alpha

    @alpha.setter
    def alpha(self, value: float):
        """Set a new transparency level for the entity."""
        if 0.0 <= value <= 1.0:
            self.__alpha = value
        else:
            raise ValueError("Alpha must be between 0.0 and 1.0.")

    @property
    def collision(self) -> bool:
        """Get the collision status of the entity."""
        return self.__collision

    @collision.setter
    def collision(self, value: bool):
        """Set the collision status for the entity."""
        if isinstance(value, bool):
            self.__collision = value
        else:
            raise ValueError("Collision must be a boolean.")

    @property
    def moveable(self) -> bool:
        """Get the moveable status of the entity."""
        return self.__moveable

    @moveable.setter
    def moveable(self, value: bool):
        """Set the moveable status for the entity."""
        if isinstance(value, bool):
            self.__moveable = value
        else:
            raise ValueError("Moveable must be a boolean.")

    def add_connector(self, connector):
        """
        Add a connector to the entity.

        :param connector: The connector to add.
        """
        self.__connector.append(connector)

    def remove_connector(self, connector):
        """
        Remove a connector from the entity.

        :param connector: The connector to remove.
        """
        if connector in self.__connector:
            self.__connector.remove(connector)
        else:
            raise ValueError("Connector not found.")

    def get_connectors(self) -> List:
        """
        Get the list of connectors.

        :return: List of connectors.
        """
        return self.__connector

    @property
    def velocity(self) -> np.ndarray:
        """Get the current velocity of the robot."""
        return self.__velocity

    @velocity.setter
    def velocity(self, new_velocity: Union[List[float], tuple, np.ndarray]):
        """Set a new velocity for the robot."""
        self.__velocity = np.array(new_velocity, dtype=float)

    @property
    def max_speed(self) -> float:
        """Get the maximum speed of the leader."""
        return self.__max_speed

    @max_speed.setter
    def max_speed(self, value: float):
        """Set a new maximum speed for the leader."""
        self.__max_speed = value

    @property
    def mass(self) -> float:
        """Get the mass of the entity."""
        return self.__mass

    @mass.setter
    def mass(self, value: float):
        """Set the mass of the entity."""
        if value > 0:
            self.__mass = value
        else:
            raise ValueError("Mass must be a positive value.")

    def move(self, dt):
        """Move the entity based on its velocity, ensuring no collisions."""
        if not self.moveable:
            return

        if self.__connector:
            total_mass = self.mass + sum(connector.mass for connector in self.__connector)
            weighted_velocity = (self.velocity * self.mass + sum(
                connector.velocity * connector.mass for connector in self.__connector)) / total_mass
            self.__velocity = weighted_velocity
        new_position = self.position + self.velocity * dt
        self.position = new_position

    def check_circle_rectangle_collision(self, rect, circle_position):
        """Check if a circle and rectangle are colliding."""
        circle_center = circle_position
        rect_center = rect.position
        rect_half_size = np.array(rect.size) / 2

        # Find the closest point to the circle within the rectangle
        closest_point = np.clip(circle_center, rect_center - rect_half_size, rect_center + rect_half_size)

        # Calculate the distance between the circle's center and this closest point
        distance = np.linalg.norm(circle_center - closest_point)

        return distance < self.size


class Obstacle(Entity):
    def __init__(self, obstacle_id, initial_position, size):
        super().__init__(obstacle_id,
                         initial_position,
                         size,
                         color="gray",
                         collision=True,
                         moveable=False)


class Landmark(Entity):
    def __init__(self, landmark_id, initial_position, size, color):
        super().__init__(landmark_id,
                         initial_position,
                         size,
                         color=color,
                         collision=False,
                         moveable=False)


class Robot(Entity):
    def __init__(self, robot_id, initial_position, size, target_position=None, color='green'):
        super().__init__(robot_id,
                         initial_position,
                         size,
                         color=color,
                         collision=True,
                         moveable=True)

        self.__target_position = np.array(target_position, dtype=float) if target_position is not None else None

    def connected_to(self, entity):
        """
        Connect the robot to another entity.
        :param entity: The entity to connect to.
        """
        self.add_connector(entity)
        entity.add_connector(self)

    def disconnect_from(self, entity):
        """
        Disconnect the robot from another entity.
        :param entity: The entity to disconnect from.
        """
        self.remove_connector(entity)
        entity.remove_connector(self)

    @property
    def target_position(self):
        """Get the target position of the robot."""
        if self.__target_position is None:
            raise ValueError("Target position not set.")
        return self.__target_position

    @target_position.setter
    def target_position(self, value):
        """Set a new target position for the robot."""
        self.__target_position = value


class PushableObject(Entity):
    def __init__(self, object_id, initial_position, size):
        super().__init__(object_id,
                         initial_position,
                         size,
                         color='yellow',
                         collision=True,
                         moveable=True)


class Leader(Entity):
    def __init__(self, leader_id, initial_position, size):
        super().__init__(leader_id, initial_position, size, color='red')
