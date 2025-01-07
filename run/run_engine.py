from modules.deployment.gymnasium_env import GymnasiumAggregationEnvironment, GymnasiumEncirclingEnvironment, \
    GymnasiumFlockingEnvironment

if __name__ == "__main__":
    import time
    import rospy

    from modules.deployment.utils.manager import Manager
    from run.auto_runner.core import EnvironmentManager

    env = GymnasiumEncirclingEnvironment("../config/real_env/encircling_config.json")
    env_manager = EnvironmentManager(env)
    env_manager.start_environment(experiment_path=".", render_mode='human')

    rospy.spin()
