ROBOT_API = """
def get_position():
    '''
    Description: Get the position of robot itself.
    Returns:
    - numpy.ndarray: The position of the robot itself.
    Usage:
    pos = get_position()
    x, y = pos[0], pos[1]
    '''

def set_velocity(velocity):
    '''
    Description: Set the velocity of the robot itself
    Input:
    - velocity (numpy.ndarray): The new velocity to set.
    Usage: 
    velocity = [vx, vy]
    set_velocity(velocity)
    '''

def get_velocity():
    '''
    Get the velocity of the robot.
    Returns:
    - numpy.ndarray: The velocity of the robot.
    '''

def gather_field_view_data():
    '''
    Description: Get the other robots' positions and velocities within the field of view.
    Returns:
    - A list of dictionaries, each containing:
      - 'position': A numpy array representing the robot's 2D position (x, y coordinates).
      - 'velocity': A numpy array representing the robot's 2D velocity (x, y components).
    if the robot is not able to observe any other robots, an empty list is returned.
    Usage: 
    robots = gather_field_view_data()
    if robots:
        for robot in robots:
            pos = robot['position']
            vel = robot['velocity']       
    '''
""".strip()

LEADER_API = """
def get_leader_position():
    '''
    Get the position of the leader robot.

    Returns:
    - numpy.ndarray: The position of the leader robot.
    '''
""".strip()


def get_robot_api(leader=False):
    if leader:
        return ROBOT_API + LEADER_API
