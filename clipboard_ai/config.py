import json
import os
from appdirs import user_config_dir
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_dir = os.path.join(user_config_dir(), "clipboard_ai")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "processing_mode": "manual",  # "auto" or "manual"
            "hotkey": "ctrl+shift+u",
            "notes_hotkey": "ctrl+shift+.",  # New hotkey for notes
            "image_hotkey": "ctrl+shift+,",  # New hotkey for image processing
            "selected_model": "deepseek-r1:8b",
            "image_model": "llava:latest",
            "ollama_host": "http://localhost:11434",
            "notification_duration": 5000,  # milliseconds
            "history_enabled": True,
            "max_history_items": 100
        }
        self.current_config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.current_config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.current_config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        self.current_config[key] = value
        self.save_config()

# Global config instance
config = Config()