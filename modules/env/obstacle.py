import numpy as np

class Entity:
    def __init__(self, entity_id, initial_position):
        self._id = entity_id
        self._position = np.array(initial_position, dtype=float)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = np.array(value, dtype=float)

    @property
    def id(self):
        return self._id


class Obstacle(Entity):
    def __init__(self, obstacle_id, initial_position, radius):
        super().__init__(obstacle_id, initial_position)
        self._radius = radius

    @property
    def radius(self):
        return self._radius


class Obstacles:
    def __init__(self, n_obstacles, size):
        self._obstacles = self.create_obstacles(n_obstacles, size)

    @property
    def obstacles(self):
        return self._obstacles

    @staticmethod
    def create_obstacles(n_obstacles, size):
        obstacle_list = []
        for i in range(n_obstacles):
            repeat_time = 0
            while True:
                repeat_time += 1
                if repeat_time > 5:
                    break
                position = np.random.uniform(-0.5, 0.5, size=2) * size
                radius = np.random.uniform(0.2, 1.0)
                new_obstacle = Obstacle(i, position, radius=radius)
                overlap = False
                for obstacle in obstacle_list:
                    distance = np.linalg.norm(new_obstacle.position - obstacle.position)
                    if distance < (new_obstacle.radius + obstacle.radius + 0.5):
                        overlap = True
                        break
                if not overlap:
                    obstacle_list.append(new_obstacle)
                    break

        return obstacle_list

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    obstacle_list = Obstacles(10, 8)._obstacles
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Obstacles')

    for obstacle in obstacle_list:
        circle = plt.Circle(obstacle.position, obstacle.radius, color='red', alpha=0.5)
        ax.add_artist(circle)
        #ax.text(obstacle.position[0], obstacle.position[1] + obstacle.radius, f'Radius: {obstacle.radius:.2f}', ha='center')

    plt.grid(True)
    plt.show()


