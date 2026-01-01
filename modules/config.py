import os
import json

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")

class ConfigManager:
    @staticmethod
    def load():
        if not os.path.exists(CONFIG_FILE):
            return {
                "skill": 20, "depth": 15, "min_delay": 0.5, "max_delay": 2.0,
                "resign_threshold": -800, "auto_newgame": False, 
                "autoplay": False, "panic": True, "auto_resign": False
            }
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def save(data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)