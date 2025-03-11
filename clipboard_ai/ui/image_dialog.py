from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QFrame, QApplication, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

class ImageDialog(QDialog):
    notes_submitted = pyqtSignal(str)  # Signal emitted when notes are submitted

    def __init__(self, image: QImage, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowTitle("Image Analysis")
        self.image = image
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
        self.resize(600, 500)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Image preview
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_label = QLabel("Captured Image:")
        preview_label.setObjectName("previewLabel")
        preview_layout.addWidget(preview_label)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setObjectName("imagePreview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Scale the image to fit within the dialog while maintaining aspect ratio
        pixmap = QPixmap.fromImage(self.image)
        # Ensure the painter is properly cleaned up
        scaled_pixmap = pixmap.scaled(
            400, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        # Process events to ensure proper cleanup
        QApplication.processEvents()
        
        preview_layout.addWidget(self.image_label)
        layout.addWidget(preview_frame)

        # Notes input
        notes_label = QLabel("What would you like to know about this image?")
        notes_label.setObjectName("notesLabel")
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("notesInput")
        self.notes_input.setPlaceholderText("Type your questions or instructions here...")
        layout.addWidget(self.notes_input)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Submit button
        self.submit_btn = QPushButton("Analyze Image")
        self.submit_btn.setObjectName("submitButton")
        self.submit_btn.clicked.connect(self.handle_submit)
        buttons_layout.addWidget(self.submit_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def handle_submit(self):
        """Handle notes submission."""
        notes = self.notes_input.toPlainText().strip()
        if notes:
            # Disable submit button to prevent multiple submissions
            self.submit_btn.setEnabled(False)
            self.submit_btn.setText("Processing...")
            # Hide immediately
            self.hide()
            # Process events to ensure dialog is hidden
            QApplication.processEvents()
            # Emit signal and close dialog
            self.notes_submitted.emit(notes)
            # Process events again before accepting
            QApplication.processEvents()
            self.accept()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and \
           event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.handle_submit()
        else:
            super().keyPressEvent(event)

    def get_stylesheet(self):
        return """
            QDialog {
                background: #1e1e2e;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            #previewFrame {
                background: #252535;
                border-radius: 8px;
                padding: 15px;
            }
            #previewLabel {
                color: #7c7cff;
                font-weight: bold;
            }
            #imagePreview {
                background: #1e1e2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                min-height: 200px;
            }
            #notesInput {
                background: #252535;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
                font-size: 13px;
                min-height: 100px;
            }
            #submitButton {
                background: #7c7cff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
            }
            #submitButton:hover {
                background: #6b6be5;
            }
        """