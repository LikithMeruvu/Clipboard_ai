from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QObject
from .settings_dialog import SettingsDialog
from ..config import config

class SystemTray(QSystemTrayIcon):
    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.app = app
        self.init_ui()
        
        # Initialize state
        self.is_paused = False
        self.settings_dialog = None

    def init_ui(self):
        """Initialize the system tray UI."""
        # Create the tray icon using the application's style
        self.setIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create the tray menu
        self.menu = QMenu()
        
        # Add menu items
        self.pause_action = self.menu.addAction("Pause")
        self.pause_action.setCheckable(True)
        self.pause_action.triggered.connect(self.toggle_pause)
        
        self.menu.addSeparator()
        
        # Settings and quit actions
        self.settings_action = self.menu.addAction("Settings")
        self.settings_action.triggered.connect(self.show_settings)
        
        self.menu.addSeparator()
        
        self.quit_action = self.menu.addAction("Quit")
        self.quit_action.triggered.connect(self.app.quit)
        
        # Set the tray's context menu
        self.setContextMenu(self.menu)
        
        # Show the tray icon
        self.show()
        
        # Show a welcome message
        self.showMessage(
            "Clipboard AI",
            "Clipboard AI is running in the background\nUse Ctrl + Shift + U to process text",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def toggle_pause(self, checked: bool):
        """Toggle the pause state."""
        self.is_paused = checked
        if hasattr(self, 'pause_callback'):
            self.pause_callback(self.is_paused)

    def change_mode(self, mode: str):
        """Change the processing mode."""
        config.set("processing_mode", mode)
        self.auto_action.setChecked(mode == "auto")
        self.manual_action.setChecked(mode == "manual")
        if hasattr(self, 'mode_change_callback'):
            self.mode_change_callback(mode)

    def show_settings(self):
        """Show the settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog()
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def show_notification(self, title: str, message: str, duration: int = None):
        """Show a notification message."""
        if duration is None:
            duration = config.get("notification_duration", 5000)
        
        self.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            duration
        )

    def set_pause_callback(self, callback):
        """Set the callback for pause/resume events."""
        self.pause_callback = callback

    def set_mode_change_callback(self, callback):
        """Set the callback for mode change events."""
        self.mode_change_callback = callback 