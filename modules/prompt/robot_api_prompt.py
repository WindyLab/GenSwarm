from modules.framework.response.code_parser import CodeParser

robot_api = """
def get_position():
    '''
    Description: Get the current position of the robot itself in real-time.
    Returns:
    - numpy.ndarray: The current, real-time position of the robot.
    '''

def set_velocity(velocity):
    '''
    Description: Set the velocity of the robot itself in real-time.
    Note: This API updates at a fixed rate of 10Hz to the vehicle, so there's no need to use time.sleep to limit the frequency, as the provided API has already implemented this.
    Input:
    - velocity (numpy.ndarray): The new velocity to be set immediately.
    '''

def get_velocity():
    '''
    Get the current velocity of the robot itself in real-time.
    Returns:
    - numpy.ndarray: The current, real-time velocity of the robot.
    '''

def get_radius():
    '''
    Description: Get the radius of the robot itself.
    Returns:
    - float: The radius of the robot itself.
    '''
    
def get_surrounding_robots_info():
    '''
    Get real-time information of the surrounding robots. 
    Note: This API is provided by humans. There is no need to concern yourself with how it is implemented; you only need to call it.
    Returns:
    - list: A list of dictionaries, each containing the current position, velocity, and radius of a robot, reflecting real-time data.
        - id (int): The unique ID of the robot.
        - position (numpy.ndarray): The current position of the robot.
        - velocity (numpy.ndarray): The current velocity of the robot.
        - radius (float): The radius of the robot.
    '''

def get_surrounding_obstacles_info():
    '''
    Get real-time information of the surrounding obstacles. 
    Note: This API is provided by humans. There is no need to concern yourself with how it is implemented; you only need to call it.
    Returns:
    - list: A list of dictionaries, each containing the current position and radius of an obstacle, reflecting real-time data.
        - id (int): The unique ID of the obstacle.
        - position (numpy.ndarray): The current position of the obstacle.
        - radius (float): The radius of the obstacle.
    '''

def get_self_id():
    '''
    Description: Get the unique ID of the robot itself.
    Returns:
    - int: The unique ID of the robot itself.
    '''
    
def get_robots_count():
    '''
    Get the total number of robots on the entire map.
    Returns:
        - count (int): The number of robots.
    '''

""".strip()

add = """

def get_target_formation_points():
    '''
    Description: Get the target formation points for the robot to reach.
    Returns:
    - list: A list of numpy.ndarray,all of which form the target formation,each representing a target point for one robot to reach.
        - position (numpy.ndarray): The position of the target formation point.
    '''
    
def get_target_position():
    '''
    Description: Get the target position for the robot to reach.
    Returns:
    - numpy.ndarray: The current position of the target.
    '''

def get_prey_position():
    '''
    Description: Get the position of the prey.
    Returns:
    - numpy.ndarray: The position of the prey.
    '''

def get_self_id():
    '''
    Description: Get the unique ID of the robot itself.
    Returns:
    - int: The unique ID of the robot itself.
    '''


def get_sheep_positions():
    '''
    Description: Get the positions of all the sheep in the environment.
    Returns:
    - list: A list of numpy.ndarray, each representing the position of a sheep.
        - position (numpy.ndarray): The position of a sheep.
    '''

"""


# data_api = read_file("modules/env/", filename="data_apis.py")


class RobotApi:
    def __init__(self, content):
        self.content = content
        code_obj = CodeParser()
        code_obj.parse_code(content)
        self.apis = code_obj.function_defs

    def get_prompt(self, name: list[str] | str = None) -> str:
        if isinstance(name, str):
            name = [name]
        if name is None:
            return "\n\n".join(self.apis.values())
        try:
            prompts = [self.apis[n] for n in name]
            return "\n\n".join(prompts)
        except Exception as e:
            raise SystemExit(
                f"Error in get_prompt: {e},current existing apis:{self.apis.keys()},input name:{name}"
            )


robot_api = RobotApi(content=robot_api)
ROBOT_API = robot_api.get_prompt()
# data_api = RobotApi(content=data_api)
# DATA_API = data_api.get_prompt()
