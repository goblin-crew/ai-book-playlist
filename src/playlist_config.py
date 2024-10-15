import os
import json
from typing import Dict, List

CONFIG_DIR = "configs"

def save_config(config: Dict, filename: str) -> None:
    """Save configuration to a JSON file."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    filepath = os.path.join(CONFIG_DIR, f"{filename}.json")
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {filepath}")

def load_config(filename: str) -> Dict:
    """Load configuration from a JSON file."""
    filepath = os.path.join(CONFIG_DIR, f"{filename}.json")
    with open(filepath, 'r') as f:
        return json.load(f)

def list_config_files() -> List[str]:
    """List available configuration files."""
    if not os.path.exists(CONFIG_DIR):
        return []
    return [f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith('.json')]

def select_config_file() -> str:
    """Prompt user to select a configuration file."""
    config_files = list_config_files()
    if not config_files:
        print("No configuration files found.")
        return None
    
    print("Available configuration files:")
    for i, filename in enumerate(config_files, 1):
        print(f"{i}. {filename}")
    
    while True:
        try:
            choice = int(input("Enter the number of the configuration file to use: "))
            if 1 <= choice <= len(config_files):
                return config_files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
