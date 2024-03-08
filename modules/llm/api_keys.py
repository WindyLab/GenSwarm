import yaml
import os
import random

class APIKeyManager:
    """
    A singleton class for managing API keys.

    This class provides functionality to allocate random API keys
    from the available keys read from a configuration file.

    Methods:
        allocate_key(): Allocate a random API key from the available keys.
    """
    _instance = None

    def __new__(cls, keys_dict):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance._load_keys(keys_dict)
        return cls._instance

    def _load_keys(self, keys_dict):
        """
        Load API keys from the provided dictionary.

        Args:
            keys_dict (dict): A dictionary containing API keys.
        """
        self._available_keys = list(keys_dict.values())

    def allocate_key(self):
        """
        Allocate a random API key from the available keys.

        Returns:
            str: The allocated API key.
        """
        if not self._available_keys:
          allocated_key = _api_key
        else:
          # allocated_key = random.choice(self._available_keys)
          allocated_key = self._available_keys[12]
          self._available_keys.remove(allocated_key)
        return allocated_key

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '../../config/api_data/keys.yml')

try:
    with open(_config_path, 'r') as config_file:
        _config = yaml.safe_load(config_file)
        api_base = _config.get('api_base', '')
        _keys_dict = _config.get('api_keys', '')
except FileNotFoundError:
    print(f"Error: Configuration file '{_config_path}' not found.")
    api_base = os.getenv('API_BASE')
    _api_key = os.getenv('API_KEY')
    _keys_dict = {}

    
key_manager = APIKeyManager(_keys_dict)

if __name__ == "__main__":
    for ind in range(100):
        key = key_manager.allocate_key()
        print(f"Allocated key {ind + 1}: {key}")