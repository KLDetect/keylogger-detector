import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    config = {}

    # Check if the configuration file exists
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading configuration: {e}")

    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        print(f"Error saving configuration: {e}")

# Load the configuration
config_data = load_config()

# Access and modify the settings
whitelist = config_data.get('whitelist', [])
autokill_list = config_data.get('autokill_list', [])
other_setting = config_data.get('other_setting')

# Add a process to the whitelist
whitelist.append(9999)

# Remove a process from the autokill list
if 1234 in autokill_list:
    autokill_list.remove(1234)

# Modify the other_setting value
config_data['other_setting'] = 'new_value'

# Save the modified configuration back to the JSON file
save_config(config_data)

