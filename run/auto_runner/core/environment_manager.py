import os
import cv2
import imageio
import rospy
from code_llm.srv import StartEnvironment, StartEnvironmentResponse
from code_llm.srv import StopEnvironment, StopEnvironmentResponse

from modules.deployment.utils.manager import Manager


class EnvironmentManager:
    def __init__(self, env, default_fps: int = 100, max_speed: float = 1.0):
        """
        Initialize the environment manager, no longer requiring experiment path and ID in the constructor.

        Args:
            env: The environment object to manage.
            default_fps (int): Default frame rate (frames per second).
            max_speed (float): Maximum speed for the manager.
        """
        self.env = env
        self.env.reset()
        self.experiment_path = None
        self.fps = default_fps  # Default frame rate
        self.manager = Manager(self.env, max_speed=max_speed)
        self.frames = []
        self.frame_dir = None
        self.experiment_duration = 0  # Set experiment duration
        self.start_time = None
        self.timer = None
        _, infos = self.env.reset()
        self.result = self.init_result(infos)
        # Register ROS services
        rospy.Service('/start_environment', StartEnvironment, self.handle_start_environment)
        rospy.Service('/stop_environment', StopEnvironment, self.handle_stop_environment)

    def init_result(self, infos: dict) -> dict:
        """
        Initialize the result structure with information about each entity in the environment.

        Args:
            infos (dict): A dictionary containing initial information for each entity.

        Returns:
            dict: Initialized result dictionary.
        """
        result = {}
        for entity_id in infos:
            result[entity_id] = {
                "size": 0,
                "target": None,
                "trajectory": [],
                'type': '',
                'states': [],
                'dt': self.env.dt
            }
            result[entity_id]["size"] = infos[entity_id]["size"]
            result[entity_id]["target"] = infos[entity_id]["target_position"]
            result[entity_id]['type'] = infos[entity_id]['type']
            result[entity_id]["trajectory"].append(infos[entity_id]["position"])
        return result

    def handle_start_environment(self, req) -> StartEnvironmentResponse:
        """
        Handle the ROS service request to start the environment.

        Args:
            req: The service request containing the experiment path.

        Returns:
            StartEnvironmentResponse: Response indicating success.
        """
        self.start_environment(req.experiment_path)
        return StartEnvironmentResponse(success=True, message="Environment started successfully.")

    def handle_stop_environment(self, req) -> StopEnvironmentResponse:
        """
        Handle the ROS service request to stop the environment.

        Args:
            req: The service request containing the file name for saving.

        Returns:
            StopEnvironmentResponse: Response indicating success.
        """
        self.stop_environment(req.file_name)
        return StopEnvironmentResponse(success=True, message="Environment stopped successfully.")

    def start_environment(self, experiment_path: str, keep_entities=False):
        """
        Start the environment and run the experiment periodically using a timer.

        Args:
            experiment_path (str): The path where experiment data will be saved.
        """
        self.experiment_path = experiment_path
        self.reset_environment(keep_entities)
        fps_duration = 1.0 / self.fps
        secs = int(fps_duration)  # Whole seconds
        nsecs = int((fps_duration - secs) * 1e9)  # Nanoseconds

        self.timer = rospy.Timer(rospy.Duration(secs=secs, nsecs=nsecs), self.step)
        print(
            f"Environment started successfully with path: {self.experiment_path}, FPS: {self.fps}")

    def reset_environment(self, keep_entities):
        """
        Reset the environment to its initial state.
        """
        self.env.reset(keep_entity=keep_entities)
        self.manager.clear_velocity()
        self.frames.clear()
        print("Environment reset successfully.")

    def stop_environment(self, file_name: str = None, save_result: bool = True):
        """
        Stop the environment and save the recorded frames as animation files.

        Args:
            file_name (str): The name of the file to save the animations.
            save_result (bool): Whether to save the simulation data.
        """
        if self.timer:
            self.timer.shutdown()
        if save_result:
            self.save_frames_as_animations(file_name)
            self.save_simulation_data(file_name)
            print(f"Environment stopped and saved as {file_name} successfully.")
        else:
            _, infos = self.env.reset(keep_entity=True)
            self.result = self.init_result(infos)
            self.frames.clear()
            print("Environment stopped successfully without saving.")

    def save_frames_as_animations(self, file_name: str):
        """
        Save the recorded frames as GIF and MP4 animation files.

        Args:
            file_name (str): The name of the file for saving the animation.
        """
        # Save as GIF
        # gif_path = os.path.join(self.experiment_path, f"{file_name}.gif")
        # imageio.mimsave(gif_path, self.frames, fps=self.fps)
        # print(f"Saved animation as GIF at {gif_path}")

        # Save as MP4
        mp4_path = os.path.join(self.experiment_path, f"{file_name}.mp4")
        height, width, layers = self.frames[0].shape
        size = (width, height)
        out = cv2.VideoWriter(mp4_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, size)

        for i, frame in enumerate(self.frames):
            # sample frame in frame list
            # if i//10 == 0:

            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        out.release()
        print(f"Saved animation as MP4 at {mp4_path}")
        self.frames.clear()

    def save_simulation_data(self, file_name: str):
        """
        Save the simulation data as a pickle file.

        Args:
            file_name (str): The name of the file for saving the data.
        """
        import pickle
        data_path = os.path.join(self.experiment_path, f"{file_name}.pkl")
        with open(data_path, "wb") as f:
            pickle.dump(self.result, f)
        print(f"Saved simulation data as pickle at {data_path}")

    def step(self, event):
        """
        Run the experiment logic periodically.

        Args:
            event: ROS Timer event that triggers this function.
        """
        action = self.manager.robotID_velocity
        obs, reward, termination, truncation, infos = self.env.step(action=action)
        for entity_id in infos:
            if infos[entity_id]["moveable"]:
                self.result[entity_id]["trajectory"].append(infos[entity_id]["position"])
            if infos[entity_id]['state'] is not None:
                self.result[entity_id]['states'].append(infos[entity_id]['state'])
        self.frames.append(self.env.render())
        self.manager.publish_observations(infos)
