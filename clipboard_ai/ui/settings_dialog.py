# clipboard_ai/ui/settings_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QRadioButton, QPushButton, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
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
    # New signal to indicate that settings have been updated
    settings_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard AI Settings")
        self.setMinimumWidth(450)
        self.check_dependencies()
        self.init_ui()

    def check_dependencies(self):
        """Check if Ollama is installed and required models are available."""
        try:
            # Check if Ollama is available
            models = ollama.list_models()
            
            # Check for required models
            required_models = {
                'text': config.get("selected_model", "gemma3:latest"),
                'image': config.get("image_model", "gemma3:latest")
            }
            
            available_models = {model.get("name", "") for model in models}
            missing_models = []
            
            for model_type, model_name in required_models.items():
                if model_name not in available_models:
                    missing_models.append(f"{model_type.capitalize()} model: {model_name}")
            
            if missing_models:
                from PyQt6.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Missing Required Models")
                msg.setText("Some required AI models are not installed:")
                msg.setInformativeText("\n".join(missing_models))
                msg.setDetailedText(
                    "To install missing models, use the following commands in terminal:\n" +
                    "".join(f"ollama pull {required_models[model_type]}\n" 
                           for model_type in required_models 
                           if required_models[model_type] not in available_models)
                )
                msg.exec()
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Ollama Not Found")
            msg.setText("Unable to connect to Ollama")
            msg.setInformativeText(
                "Please ensure Ollama is installed and running.\n\n" 
                "Visit https://ollama.ai for installation instructions."
            )
            msg.exec()

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
        self.image_hotkey_input = QLineEdit(config.get("image_hotkey", "ctrl+shift+,"))  # default comma
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

        # Try to select the current config value for text model
        idx_text = self.text_model_combo.findText(current_text_model)
        if idx_text >= 0:
            self.text_model_combo.setCurrentIndex(idx_text)
        else:
            self.text_model_combo.insertItem(0, current_text_model)
            self.text_model_combo.setCurrentIndex(0)

        # Try to select the current config value for image model
        idx_image = self.image_model_combo.findText(current_image_model)
        if idx_image >= 0:
            self.image_model_combo.setCurrentIndex(idx_image)
        else:
            self.image_model_combo.insertItem(0, current_image_model)
            self.image_model_combo.setCurrentIndex(0)

    def save_settings(self):
        """Save the current settings to config and notify the main app to update state."""
        # ===== Processing Mode =====
        mode = "auto" if self.auto_mode.isChecked() else "manual"
        config.set("processing_mode", mode)

        # ===== Hotkeys =====
        text_hotkey = self.text_hotkey_input.text().strip() or "ctrl+shift+u"
        config.set("hotkey", text_hotkey)

        image_hotkey = self.image_hotkey_input.text().strip() or "ctrl+shift+o "  # default comma
        config.set("image_hotkey", image_hotkey)

        # ===== Models =====
        selected_text_model = self.text_model_combo.currentText() or "deepseek-r1:8b"
        config.set("selected_model", selected_text_model)

        selected_image_model = self.image_model_combo.currentText() or "llava:latest"
        config.set("image_model", selected_image_model)

        # Emit a signal so the main application can re-register hotkeys and update its state
        self.settings_updated.emit()
        self.accept()
