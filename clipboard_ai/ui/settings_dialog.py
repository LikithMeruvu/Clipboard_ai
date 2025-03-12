# clipboard_ai/ui/settings_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QRadioButton, QPushButton, QButtonGroup,
    QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from ..config import config
from ..ollama_integration import ollama

class SettingsDialog(QDialog):
    """
    Settings dialog that lets the user:
      1. Switch between Auto/Manual processing modes
      2. Choose a text model and an image model separately
      3. Change the hotkeys for text and image
      4. (Optional) Refresh the list of Ollama models
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard AI Settings")
        self.setMinimumWidth(450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ===== Processing Mode Group =====
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QVBoxLayout()

        self.auto_mode = QRadioButton("Auto Process")
        self.manual_mode = QRadioButton("Manual (Hotkey)")
        current_mode = config.get("processing_mode", "manual")

        self.auto_mode.setChecked(current_mode == "auto")
        self.manual_mode.setChecked(current_mode == "manual")

        mode_layout.addWidget(self.auto_mode)
        mode_layout.addWidget(self.manual_mode)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # ===== Hotkey Configuration =====
        hotkey_group = QGroupBox("Hotkey Configuration")
        hotkey_layout = QVBoxLayout()

        # Text hotkey
        text_hotkey_layout = QHBoxLayout()
        text_hotkey_label = QLabel("Text Hotkey:")
        self.text_hotkey_input = QLineEdit(config.get("hotkey", "ctrl+shift+u"))
        text_hotkey_layout.addWidget(text_hotkey_label)
        text_hotkey_layout.addWidget(self.text_hotkey_input)
        hotkey_layout.addLayout(text_hotkey_layout)

        # Image hotkey
        image_hotkey_layout = QHBoxLayout()
        image_hotkey_label = QLabel("Image Hotkey:")
        self.image_hotkey_input = QLineEdit(config.get("image_hotkey", "ctrl+shift+,"))
        image_hotkey_layout.addWidget(image_hotkey_label)
        image_hotkey_layout.addWidget(self.image_hotkey_input)
        hotkey_layout.addLayout(image_hotkey_layout)

        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # ===== Model Selection =====
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()

        # Text Model
        text_model_layout = QHBoxLayout()
        text_model_label = QLabel("Text Model:")
        self.text_model_combo = QComboBox()
        text_model_layout.addWidget(text_model_label)
        text_model_layout.addWidget(self.text_model_combo)
        model_layout.addLayout(text_model_layout)

        # Image Model
        image_model_layout = QHBoxLayout()
        image_model_label = QLabel("Image Model:")
        self.image_model_combo = QComboBox()
        image_model_layout.addWidget(image_model_label)
        image_model_layout.addWidget(self.image_model_combo)
        model_layout.addLayout(image_model_layout)

        # Refresh button
        refresh_button = QPushButton("Refresh Models")
        refresh_button.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_button)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # ===== Buttons =====
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initialize combos with current settings
        self.refresh_models()

    def refresh_models(self):
        """Refresh the list of available models and populate both combos."""
        # Clear combos
        self.text_model_combo.clear()
        self.image_model_combo.clear()

        # Retrieve all models from Ollama
        models = ollama.list_models()

        # Current selections from config
        current_text_model = config.get("selected_model", "deepseek-r1:8b")
        current_image_model = config.get("image_model", "llava:latest")

        # Populate combos
        for model in models:
            model_name = model.get("name", "")
            # Add to both combos
            self.text_model_combo.addItem(model_name)
            self.image_model_combo.addItem(model_name)

        # Try to select the current config value
        idx_text = self.text_model_combo.findText(current_text_model)
        if idx_text >= 0:
            self.text_model_combo.setCurrentIndex(idx_text)
        else:
            # If not found, insert it as a fallback
            self.text_model_combo.insertItem(0, current_text_model)
            self.text_model_combo.setCurrentIndex(0)

        idx_image = self.image_model_combo.findText(current_image_model)
        if idx_image >= 0:
            self.image_model_combo.setCurrentIndex(idx_image)
        else:
            self.image_model_combo.insertItem(0, current_image_model)
            self.image_model_combo.setCurrentIndex(0)

    def save_settings(self):
        """Save the current settings to config and re-register hotkeys if needed."""
        # ===== Processing Mode =====
        mode = "auto" if self.auto_mode.isChecked() else "manual"
        config.set("processing_mode", mode)

        # ===== Hotkeys =====
        text_hotkey = self.text_hotkey_input.text().strip()
        if not text_hotkey:
            # Default if empty
            text_hotkey = "ctrl+shift+u"
            self.text_hotkey_input.setText(text_hotkey)
        config.set("hotkey", text_hotkey)

        image_hotkey = self.image_hotkey_input.text().strip()
        if not image_hotkey:
            image_hotkey = "ctrl+shift+,"
            self.image_hotkey_input.setText(image_hotkey)
        config.set("image_hotkey", image_hotkey)

        # ===== Models =====
        selected_text_model = self.text_model_combo.currentText()
        if not selected_text_model:
            selected_text_model = "deepseek-r1:8b"
        config.set("selected_model", selected_text_model)

        selected_image_model = self.image_model_combo.currentText()
        if not selected_image_model:
            selected_image_model = "llava:latest"
        config.set("image_model", selected_image_model)

        self.accept()
