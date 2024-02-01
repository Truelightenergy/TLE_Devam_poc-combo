import os
import yaml
current_path = os.path.dirname(os.path.abspath(__file__))

def read_config():
    config = None
    # Read data from YAML file
    file_name = 'config.yml'
    file_path = os.path.join(current_path, file_name)
    with open(file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config
