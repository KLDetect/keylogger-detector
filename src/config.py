import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    """
    Load the configuration from the JSON file or create a new one if it doesn't exist

    Returns:
        dict: The configuration data
    """
    config = {}

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
        except:
            print("[-] Error: Failed to load config file")
    else:
        config = {
            'white_listed_programs': [],
            'auto_kill_programs': [],
            'kbd_names': ['kbd']
        }
        save_config(config)

    return config


def save_config(config):
    """
    Save the configuration to the JSON file

    Args:
        config (dict): The configuration data
    """
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
    except:
        print("[-] Error: Failed to save config file")

