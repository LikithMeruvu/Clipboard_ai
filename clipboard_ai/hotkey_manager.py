import keyboard
from typing import Callable
from .config import config
from PyQt6.QtCore import QObject

class HotkeyManager(QObject):
    def __init__(self):
        super().__init__()
        self._callback: Callable[[], None] = lambda: None
        self._current_hotkey = None
        self._is_registered = False

    def register_hotkey(self, callback: Callable[[], None], hotkey: str = None) -> None:
        """Register the hotkey with the given callback."""
        self._callback = callback
        self._current_hotkey = hotkey or config.get("hotkey")
        self._register_current_hotkey()

    def _register_current_hotkey(self) -> None:
        """Register the current hotkey configuration."""
        if self._is_registered:
            self.unregister_hotkey()
        
        # Validate that hotkey is not empty
        if not self._current_hotkey or self._current_hotkey.strip() == "":
            print("Error: Cannot register empty hotkey")
            self._is_registered = False
            return
            
        try:
            keyboard.add_hotkey(self._current_hotkey, self._callback)
            self._is_registered = True
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            self._is_registered = False

    def unregister_hotkey(self) -> None:
        """Unregister the current hotkey."""
        if self._current_hotkey and self._is_registered:
            try:
                keyboard.remove_hotkey(self._current_hotkey)
                self._is_registered = False
            except:
                pass

    def update_hotkey(self, new_hotkey: str) -> bool:
        """Update the hotkey combination."""
        try:
            old_hotkey = self._current_hotkey
            self._current_hotkey = new_hotkey
            
            if self._is_registered:
                self.unregister_hotkey()
                self._register_current_hotkey()
            
            return True
        except Exception as e:
            print(f"Error updating hotkey: {e}")
            self._current_hotkey = old_hotkey
            return False

    def get_current_hotkey(self) -> str:
        """Get the current hotkey combination."""
        return self._current_hotkey