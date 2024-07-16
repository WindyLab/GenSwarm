import os

import yaml


class ModelManager:
    """
    A singleton class for managing API keys.

    This class provides functionality to allocate random API keys
    from the available keys read from a configuration file.

    Methods:
        allocate_key(): Allocate a random API key from the available keys.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            _current_dir = os.path.dirname(os.path.abspath(__file__))
            _config_path = os.path.join(_current_dir, "../../config/llm_config2.yml")
            try:
                with open(_config_path, "r") as config_file:
                    cls._config = yaml.safe_load(config_file)
            except FileNotFoundError:
                print(f"Error: Configuration file '{_config_path}' not found.")
        return cls._instance

    def allocate(self, model_family: str = "QWEN"):
        api_base = self._config["api_base"][model_family]
        api_key = self._config["api_key"][model_family]
        model = self._config["model"][model_family]
        return api_base, api_key, model


model_manager = ModelManager()

if __name__ == "__main__":
    print(model_manager.allocate(model_family="QWEN"))
