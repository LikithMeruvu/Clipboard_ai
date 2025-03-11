from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal

class NotesDialog(QDialog):
    notes_submitted = pyqtSignal(str)  # Signal emitted when notes are submitted

    def __init__(self, copied_text: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowTitle("Add Notes")
        self.copied_text = copied_text
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
        self.resize(500, 400)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Preview of copied content
        preview_frame = QFrame()
        preview_frame.setObjectName("previewFrame")
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_label = QLabel("Copied Content:")
        preview_label.setObjectName("previewLabel")
        preview_layout.addWidget(preview_label)
        
        content_preview = QTextEdit()
        content_preview.setObjectName("contentPreview")
        content_preview.setPlainText(self.copied_text)
        content_preview.setReadOnly(True)
        content_preview.setMaximumHeight(100)
        preview_layout.addWidget(content_preview)
        
        layout.addWidget(preview_frame)

        # Notes input
        notes_label = QLabel("Add your notes or questions about this content:")
        notes_label.setObjectName("notesLabel")
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("notesInput")
        self.notes_input.setPlaceholderText("Type your notes here...")
        layout.addWidget(self.notes_input)

        # Submit button
        self.submit_btn = QPushButton("Submit Notes")
        self.submit_btn.setObjectName("submitButton")
        self.submit_btn.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def handle_submit(self):
        """Handle notes submission."""
        notes = self.notes_input.toPlainText().strip()
        if notes:
            # Hide immediately
            self.hide()
            # Process events to ensure dialog is hidden
            QApplication.processEvents()
            # Emit signal and close
            self.notes_submitted.emit(notes)
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
            #contentPreview {
                background: #1e1e2e;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
                font-size: 13px;
            }
            #notesInput {
                background: #252535;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
                font-size: 13px;
                min-height: 150px;
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