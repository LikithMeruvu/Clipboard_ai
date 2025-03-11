from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QRadioButton, QPushButton, QButtonGroup,
                             QLineEdit, QGroupBox)
from PyQt6.QtCore import Qt
from ..config import config
from ..ollama_integration import ollama

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard AI Settings")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Processing Mode Group
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QVBoxLayout()
        
        self.auto_mode = QRadioButton("Auto Process")
        self.manual_mode = QRadioButton("Manual (Hotkey)")
        current_mode = config.get("processing_mode")
        
        self.auto_mode.setChecked(current_mode == "auto")
        self.manual_mode.setChecked(current_mode == "manual")
        
        mode_layout.addWidget(self.auto_mode)
        mode_layout.addWidget(self.manual_mode)
        mode_group.setLayout(mode_layout)
        
        # Hotkey Configuration
        hotkey_group = QGroupBox("Hotkey Configuration")
        hotkey_layout = QHBoxLayout()
        
        self.hotkey_input = QLineEdit(config.get("hotkey"))
        self.hotkey_input.setPlaceholderText("Enter hotkey combination")
        
        hotkey_layout.addWidget(QLabel("Hotkey:"))
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_group.setLayout(hotkey_layout)
        
        # Model Selection
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        self.refresh_models()
        
        model_layout.addWidget(QLabel("Select Model:"))
        model_layout.addWidget(self.model_combo)
        
        refresh_button = QPushButton("Refresh Models")
        refresh_button.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_button)
        
        model_group.setLayout(model_layout)
        
        # Add all groups to main layout
        layout.addWidget(mode_group)
        layout.addWidget(hotkey_group)
        layout.addWidget(model_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def refresh_models(self):
        """Refresh the list of available models."""
        self.model_combo.clear()
        models = ollama.list_models()
        current_model = config.get("selected_model")
        
        for model in models:
            model_name = model.get("name", "")
            self.model_combo.addItem(model_name)
            
            if model_name == current_model:
                self.model_combo.setCurrentText(model_name)

    def save_settings(self):
        """Save the current settings."""
        # Save processing mode
        mode = "auto" if self.auto_mode.isChecked() else "manual"
        config.set("processing_mode", mode)
        
        # Save hotkey - validate it's not empty
        hotkey = self.hotkey_input.text().strip()
        if not hotkey:
            # Set a default hotkey if empty
            hotkey = "ctrl+shift+u"
            self.hotkey_input.setText(hotkey)
        config.set("hotkey", hotkey)
        
        # Save selected model
        config.set("selected_model", self.model_combo.currentText())
        
        self.accept()