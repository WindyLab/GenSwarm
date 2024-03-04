import datetime
import threading
from pathlib import Path


ENV_DES = '''
below are the basic information of the environment and robots:
environment:
    size: 10m x 10m
    Obstacles: None
    X-axis: -5m to 5m
    Y-axis: -5m to 5m
    
Robots: 
    Max Speed: 2m/s
    Control: velocity control
    Max Control Frequency: 20Hz

'''

ROBOT_API = """

def get_robot_position_by_id(robot_id):
    '''
    Get the position of a robot with the given ID.

    Input:
    - robot_id(int): The ID of the robot to retrieve.

    Output:
    - numpy.ndarray(float,float) : The position of the robot.
    '''

def set_robot_velocity_by_id(robot_id, velocity):
    '''
    Set the velocity of a robot with the given ID.

    Input:
    - robot_id(int): The ID of the robot to set the velocity for.
    Output:
    -  numpy.ndarray(float,float): The new velocity to set.
    '''

def get_all_robot_ids():
    '''
    Get a list of all existing robot IDs.

    Output:
    - list[int] : A list containing all the robot IDs.
    '''
    
def get_robots_count():
    '''
    Get the total number of robots.

    Returns:
    - int: The total number of robots.
    '''
    
    
def get_leader_position():
    '''
    Get the position of the leader robot.

    Returns:
    - numpy.ndarray: The position of the leader robot.
    '''
"""
LEADER_API = """
def get_leader_position():
    '''
    Get the position of the leader robot.

    Returns:
    - numpy.ndarray: The position of the leader robot.
    '''
"""


def get_robot_api(leader=False):
    if leader:
        return ROBOT_API + LEADER_API


def get_project_root():
    """Search upwards to find the project root directory."""
    current_path = Path.cwd()
    while True:
        if (
                (current_path / ".git").exists()
                or (current_path / ".project_root").exists()
                or (current_path / ".gitignore").exists()
        ):
            # use metagpt with git clone will land here
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            # use metagpt with pip install will land here
            cwd = Path.cwd()
            return cwd
        current_path = parent_path


current_datetime = datetime.datetime.now()
formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
PROJECT_ROOT = get_project_root()
WORKSPACE_ROOT = PROJECT_ROOT / f"workspace/{formatted_date}"
DATA_PATH = WORKSPACE_ROOT / "data"
ENV_PATH = WORKSPACE_ROOT / "env"

GLOBAL_LOCK = threading.Lock()
