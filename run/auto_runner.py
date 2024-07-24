import math
import os
import threading
import subprocess
import time

import imageio
import rospy
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from modules.deployment.gymnasium_env import GymnasiumCrossEnvironment
from modules.deployment.utils.manager import Manager


class AutoRunner:
    def __init__(self, env_config_path,
                 workspace_path,
                 experiment_duration,
                 run_mode='rerun',
                 max_speed=1.0,
                 tolerance=0.05):
        self.env_config_path = env_config_path
        self.experiment_path = workspace_path
        self.experiment_duration = experiment_duration
        self.env = GymnasiumCrossEnvironment(self.env_config_path, radius=2.20)
        self.env.reset()
        self.results = {}
        self.manager = Manager(self.env, max_speed=max_speed)
        self.stop_event = threading.Event()
        self.run_mode = run_mode
        self.tolerance = tolerance
        self.frames = []

    def get_experiment_directories(self):
        directories = []
        for item in os.listdir(f"../workspace/{self.experiment_path}"):
            item_path = os.path.join(f"../workspace/{self.experiment_path}", item)
            if os.path.isdir(item_path):
                if self.run_mode == 'continue':
                    if not self.experiment_completed(item_path):
                        directories.append(item)
                elif self.run_mode == 'rerun':
                    directories.append(item)
                elif self.run_mode == 'analyze':
                    if self.experiment_completed(item_path):
                        directories.append(item)
        return directories

    def experiment_completed(self, path):
        result_file = os.path.join(path, 'result.json')
        return os.path.exists(result_file)

    def save_experiment_result(self, path, result, analysis):
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_to_serializable(i) for i in obj]
            return obj

        serializable_result = convert_to_serializable(result)
        serializable_analysis = convert_to_serializable(analysis)
        combined_result = {
            'analysis': serializable_analysis,
            'experiment_data': serializable_result,
        }
        result_file = os.path.join(path, 'result.json')
        os.makedirs(path, exist_ok=True)
        with open(result_file, 'w') as f:
            json.dump(combined_result, f, indent=4)

    def run_single_experiment(self, experiment_id):
        obs, infos = self.env.reset()

        def init_result(infos):
            result = {}
            for entity_id in infos:
                result[entity_id] = {"size": 0, "target": None, "trajectory": []}
                result[entity_id]["size"] = infos[entity_id]["size"]
                result[entity_id]["target"] = infos[entity_id]["target_position"]
                result[entity_id]["trajectory"].append(infos[entity_id]["position"])
            return result

        result = init_result(infos)
        self.manager.publish_observations(infos)
        rate = rospy.Rate(self.env.FPS)
        start_time = rospy.get_time()

        while not rospy.is_shutdown() and not self.stop_event.is_set():
            current_time = rospy.get_time()
            if current_time - start_time > self.experiment_duration:
                break
            action = self.manager.robotID_velocity
            self.manager.clear_velocity()
            obs, reward, termination, truncation, infos = self.env.step(action=action)
            for entity_id in infos:
                result[entity_id]["trajectory"].append(infos[entity_id]["position"])
            self.frames.append(self.env.render())
            self.manager.publish_observations(infos)
            rate.sleep()
        print(f"Experiment {experiment_id} completed successfully.")
        self.save_frames_as_animations(experiment_id)

        return result

    def save_frames_as_animations(self, experiment_id):
        # Save as GIF
        gif_path = os.path.join(f"../workspace/{self.experiment_path}", experiment_id, 'animation.gif')
        imageio.mimsave(gif_path, self.frames, fps=self.env.FPS)
        print(f"Saved animation for experiment {experiment_id} as GIF at {gif_path}")

        # Save as MP4
        mp4_path = os.path.join(f"../workspace/{self.experiment_path}", experiment_id, 'animation.mp4')
        height, width, layers = self.frames[0].shape
        size = (width, height)
        out = cv2.VideoWriter(mp4_path, cv2.VideoWriter_fourcc(*'mp4v'), self.env.FPS, size)

        for frame in self.frames:
            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        out.release()
        print(f"Saved animation for experiment {experiment_id} as MP4 at {mp4_path}")

        self.frames.clear()

    def analyze_result(self, run_result):
        def are_trajectories_equal_length(data):
            lengths = [len(info["trajectory"]) for info in data.values()]
            return all(length == lengths[0] for length in lengths)

        def collision_check(data, tolerance=0.1):
            target_entities = {id: info for id, info in data.items() if info["target"] is not None}

            num_timesteps = len(next(iter(data.values()))["trajectory"])
            collision_count = 0
            collision_severity_sum = 0

            for id1, info1 in target_entities.items():
                for t in range(num_timesteps):
                    pos1 = info1["trajectory"][t]
                    for id2, info2 in data.items():
                        if id1 == id2:
                            continue
                        pos2 = info2["trajectory"][t]
                        distance = math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
                        if distance + tolerance < (info1["size"] + info2["size"]):
                            collision_count += 1
                            overlap = info1["size"] + info2["size"] - distance
                            collision_severity_sum += overlap / (info1["size"] + info2["size"])

            num_target_entities = len(target_entities)
            collision_frequency = collision_count / (
                    num_target_entities * num_timesteps) if num_target_entities > 0 else 0
            collision_severity_mean = collision_severity_sum / collision_count if collision_count > 0 else 0

            return collision_count > 0, collision_frequency, collision_severity_mean, collision_severity_sum

        def target_achieve(data, tolerance=0.1):
            total_distance_ratio = 0
            achieved_targets = 0
            num_targets = 0
            total_steps_ratio = 0

            for entity_id, info in data.items():
                target = info["target"]
                if target is None:
                    continue
                num_targets += 1
                initial_position = info["trajectory"][0]
                initial_distance = math.sqrt(
                    (target[0] - initial_position[0]) ** 2 + (target[1] - initial_position[1]) ** 2)

                steps_to_target = len(info["trajectory"])
                final_distance = initial_distance
                for t, position in enumerate(info["trajectory"]):
                    current_distance = math.sqrt(
                        (target[0] - position[0]) ** 2 + (target[1] - position[1]) ** 2)
                    if current_distance <= tolerance:
                        steps_to_target = t + 1
                        final_distance = current_distance
                        break
                if final_distance <= tolerance:
                    achieved_targets += 1
                    total_steps_ratio += steps_to_target / len(info["trajectory"])
                distance_ratio = final_distance / initial_distance if initial_distance > 0 else 1
                total_distance_ratio += distance_ratio

                print(
                    f"Entity {entity_id}: Initial Distance: {initial_distance}, Final Distance: {final_distance}, Ratio: {distance_ratio}, Steps to Target: {steps_to_target}")

            target_achieve_ratio = achieved_targets / num_targets if num_targets > 0 else 0
            average_distance_ratio = total_distance_ratio / num_targets if num_targets > 0 else 0
            average_steps_ratio = total_steps_ratio / achieved_targets if achieved_targets > 0 else 'inf'

            return achieved_targets == num_targets, target_achieve_ratio, average_distance_ratio, average_steps_ratio

        if not are_trajectories_equal_length(run_result):
            raise ValueError("Trajectories have different lengths")

        collision, collision_frequency, collision_severity_mean, collision_severity_sum = collision_check(
            run_result, tolerance=self.tolerance)
        target_achieve, target_achieve_ratio, average_distance_ratio, average_steps_ratio = target_achieve(
            run_result, tolerance=2 * self.tolerance)

        return {
            'collision_occurred': collision,
            'collision_frequency': collision_frequency,
            'collision_severity_average': collision_severity_mean,
            'collision_severity_sum': collision_severity_sum,
            'target_achieved': target_achieve,
            'target_achievement_ratio': target_achieve_ratio,
            'distance_ratio_average': average_distance_ratio,
            'steps_ratio_average': average_steps_ratio
        }

    def run_and_analyze_experiment(self, experiment):
        result = self.run_single_experiment(experiment)
        analysis = self.analyze_result(result)

        print(f"Analysis for experiment {experiment}: {analysis}")
        self.results[experiment] = analysis
        self.save_experiment_result(os.path.join(f"../workspace/{self.experiment_path}", experiment), result, analysis)

    def run_code(self, experiment):
        experiment_path = os.path.join(self.experiment_path, experiment)
        command = ['python', '../modules/framework/actions/run_code.py', '--data', experiment_path, '--timeout',
                   str(self.experiment_duration - 3)]

        try:
            result = subprocess.run(command, timeout=self.experiment_duration - 2, capture_output=True, text=True,
                                    check=True)
        except subprocess.TimeoutExpired:
            print(f"\nExperiment {experiment} timed out and was terminated.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running {experiment}: {e}")
            print(f"Errors: {e.stderr}")

    def run_multiple_experiments(self):
        experiment_list = sorted(self.get_experiment_directories())

        try:
            with tqdm(total=len(experiment_list), desc="Running Experiments") as pbar:
                for experiment in experiment_list:
                    self.stop_event.clear()
                    time.sleep(1)

                    t1 = threading.Thread(target=self.run_code, args=(experiment,))
                    t2 = threading.Thread(target=self.run_and_analyze_experiment, args=(experiment,))

                    t1.start()
                    t2.start()

                    t1.join(timeout=self.experiment_duration - 1)
                    t2.join(timeout=self.experiment_duration - 1)

                    if t1.is_alive() or t2.is_alive():
                        self.stop_event.set()
                        t1.join()
                        t2.join()

                    pbar.update(1)

        except KeyboardInterrupt:
            print("Keyboard interrupt received. Stopping all experiments.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.stop_event.set()
            t1.join()
            t2.join()

        print("All experiments completed successfully.")

    def plot_and_print_results(self, data, labels, ylabel, title, colors, save_filename):
        plt.figure(figsize=(10, 6))
        plt.bar(labels, data, color=colors)
        plt.ylabel(ylabel)
        plt.title(title)
        for i, v in enumerate(data):
            plt.text(i, v + 0.01, f"{v:.2f}", ha='center')
        plt_path = os.path.join(f"../workspace/{self.experiment_path}", save_filename)
        plt.savefig(plt_path)
        plt.show()
        print(f"{title}: {data}")

    def analyze_all_results(self):
        experiment_dirs = self.get_experiment_directories()
        collision_files = []
        no_target_achieve_files = []
        no_collision_and_target_achieve = []
        collision_frequencies = []
        collision_severities = []
        distance_ratios = []
        target_achievement_ratios = []
        steps_ratios = []

        for experiment in experiment_dirs:
            result_path = os.path.join(f"../workspace/{self.experiment_path}", experiment, 'result.json')
            if os.path.exists(result_path):
                with open(result_path, 'r') as f:
                    result_data = json.load(f)
                    analysis = result_data.get('analysis', {})
                    if analysis.get('collision_occurred'):
                        collision_files.append(experiment)
                    if not analysis.get('target_achieved'):
                        no_target_achieve_files.append(experiment)
                    if not analysis.get('collision_occurred') and analysis.get('target_achieved'):
                        no_collision_and_target_achieve.append(experiment)

                    collision_frequencies.append(analysis.get('collision_frequency'))
                    collision_severities.append(analysis.get('collision_severity_sum'))
                    distance_ratios.append(analysis.get('distance_ratio_average'))

                    target_achievement_ratios.append(analysis.get('target_achievement_ratio'))
                    if analysis.get('steps_ratio_average') != 'inf':
                        steps_ratios.append(analysis.get('steps_ratio_average'))

        mean_collision_frequency = np.mean(collision_frequencies) if collision_frequencies else 0
        mean_collision_severity = np.mean(collision_severities) if collision_severities else 0
        mean_distance_ratio = np.mean(distance_ratios) if distance_ratios else 0
        mean_target_achieve_ratio = np.mean(target_achievement_ratios) if target_achievement_ratios else 0
        mean_steps_ratios = np.mean(steps_ratios) if steps_ratios else 0
        metrics = [
            ([mean_collision_frequency, mean_collision_severity], ['Collision Frequency', 'Collision Severity'],
             'Value', 'Collision Metrics', ['purple', 'orange'], 'collision_metrics.png'),
            ([mean_distance_ratio, mean_target_achieve_ratio, mean_steps_ratios],
             ['Distance Ratio', 'Target Achieve Ratio', 'Steps Ratio'], 'Ratio',
             'Distance Metrics', ['cyan', 'blue', 'green'], 'distance_metrics.png'),
        ]

        for data, labels, ylabel, title, colors, filename in metrics:
            self.plot_and_print_results(data, labels, ylabel, title, colors, filename)

        collision_rate = len(collision_files) / len(experiment_dirs) if experiment_dirs else 0
        target_achieve_rate = len(no_target_achieve_files) / len(experiment_dirs) if experiment_dirs else 0
        no_collision_and_target_rate = len(no_collision_and_target_achieve) / len(
            experiment_dirs) if experiment_dirs else 0
        self.plot_and_print_results(
            [collision_rate, target_achieve_rate, no_collision_and_target_rate],
            ['No Collision', 'Target Achieve', 'No Collision & Target Achieve'],
            'Rate',
            'Experiment Outcomes',
            ['red', 'green', 'blue'],
            'experiment_outcomes.png'
        )
        collision_files = '\n'.join(collision_files)
        no_target_achieve_files = '\n'.join(no_target_achieve_files)
        print(f"Experiments with collisions:\n{collision_files}")
        print(f"\nExperiments without target achievement:\n{no_target_achieve_files}")


if __name__ == "__main__":
    runner = AutoRunner("../config/env_config.json",
                        workspace_path='layer/cross',
                        experiment_duration=20,
                        run_mode='rerun',
                        max_speed=1.0,
                        tolerance=0.05
                        )

    if runner.run_mode in ['rerun', 'continue']:
        runner.run_multiple_experiments()

    if runner.run_mode == 'analyze':
        runner.analyze_all_results()
