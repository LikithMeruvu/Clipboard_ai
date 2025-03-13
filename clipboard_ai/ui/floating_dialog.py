from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QProgressBar, QApplication,
                             QFrame, QSplitter, QWidget, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QScreen, QColor, QPalette, QIcon, QImage, QPixmap

class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Title label
        self.title = QLabel("Clipboard AI")
        self.title.setObjectName("titleLabel")
        layout.addWidget(self.title)
        
        # Spacer
        layout.addStretch()
        
        # Window controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        # New Chat button
        self.new_chat_btn = QPushButton("+ New Chat")
        self.new_chat_btn.setObjectName("newChatBtn")
        self.new_chat_btn.clicked.connect(parent.clear_chat)
        btn_layout.addWidget(self.new_chat_btn)
        
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("minimizeBtn")
        self.minimize_btn.clicked.connect(parent.minimize)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(parent.hide)
        
        btn_layout.addWidget(self.minimize_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

class LoadingDots(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loadingDots")
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.setText("...")
        
    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.setText("." * self.dots)
        
    def start(self):
        self.timer.start(500)  # Update every 500ms
        
    def stop(self):
        self.timer.stop()
        self.setText("")

class ThinkingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("thinkingWidget")
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create thinking icon and label
        self.thinking_icon = QLabel("🤖")
        self.thinking_icon.setObjectName("thinkingIcon")
        layout.addWidget(self.thinking_icon)
        
        self.thinking_label = QLabel("Generating...")
        self.thinking_label.setObjectName("thinkingLabel")
        layout.addWidget(self.thinking_label)
        
        # Add loading dots animation
        self.loading_dots = LoadingDots()
        self.loading_dots.setObjectName("loadingDots")
        layout.addWidget(self.loading_dots)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Initialize thinking content (hidden by default)
        self.thinking_content = QTextEdit()
        self.thinking_content.setObjectName("thinkingContent")
        self.thinking_content.setReadOnly(True)
        self.thinking_content.hide()

    def start_thinking(self):
        """Start the thinking animation."""
        self.thinking_icon.setText("🤖")
        self.thinking_label.setText("Generating...")
        self.loading_dots.start()

    def stop_thinking(self):
        """Stop the thinking animation."""
        self.loading_dots.stop()
        self.thinking_icon.setText("✓")
        self.thinking_label.setText("Complete")

    def set_error(self, error_message: str):
        """Set error state."""
        self.loading_dots.stop()
        self.thinking_icon.setText("❌")
        self.thinking_label.setText("Error")

class ChatMessage(QFrame):
    def __init__(self, is_user=True, parent=None):
        super().__init__(parent)
        self.setObjectName("userMessage" if is_user else "assistantMessage")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Add header with role label and copy button
        header = QHBoxLayout()
        header.setSpacing(10)
        
        role_icon = QLabel("👤" if is_user else "🤖")
        role_icon.setObjectName("roleIcon")
        header.addWidget(role_icon)
        
        role_label = QLabel("You" if is_user else "Assistant")
        role_label.setObjectName("roleLabel")
        header.addWidget(role_label)
        
        header.addStretch()
        
        copy_btn = QPushButton("📋 Copy")
        copy_btn.setObjectName("copyButton")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self.copy_content)
        header.addWidget(copy_btn)
        
        layout.addLayout(header)
        
        # Content container
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        
        # Image preview (if any)
        self.image_label = QLabel()
        self.image_label.setObjectName("messageImage")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.hide()
        content_layout.addWidget(self.image_label)
        
        # Text content
        self.content = QLabel()
        self.content.setObjectName("messageContent")
        self.content.setWordWrap(True)
        self.content.setTextFormat(Qt.TextFormat.PlainText)
        self.content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_layout.addWidget(self.content)
        
        layout.addLayout(content_layout)

    def copy_content(self):
        """Copy message content to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content.text())
        
    def setText(self, text):
        """Set the message content."""
        self.content.setText(text)

    def setImage(self, image: QImage):
        """Set the image content."""
        if image:
            # Scale the image to fit while maintaining aspect ratio
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(
                400, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.show()
            QApplication.processEvents()

class ChatWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for messages
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setObjectName("chatScroll")
        
        # Container for messages
        self.messages_widget = QWidget()
        self.messages_widget.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(4,5,4,5)
        self.messages_layout.setSpacing(6)  # Space between messages
        self.messages_layout.addStretch()
        
        self.scroll.setWidget(self.messages_widget)
        layout.addWidget(self.scroll)
        
        # Follow-up input area
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(1,0,1,0)
        input_layout.setSpacing(5)  # Reduced spacing
        
        self.follow_up_input = QTextEdit()
        self.follow_up_input.setObjectName("followUpInput")
        self.follow_up_input.setPlaceholderText("Press Enter for new line, Shift+Enter to send")
        self.follow_up_input.setMaximumHeight(50)  # Reduced from 80 to 50
        self.follow_up_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Set fixed vertical size policy
        input_layout.addWidget(self.follow_up_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(input_container)
        
        # Store message history
        self.message_history = []

    def add_message(self, text, is_user=True, image=None):
        msg = ChatMessage(is_user)
        msg.setText(text)
        if image:
            msg.setImage(image)
        # Insert before the stretch at the end
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, msg)
        self.message_history.append((text, is_user, image))
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        return msg
    
    def restore_history(self):
        """Restore chat history from stored messages."""
        self.clear_history()
        for text, is_user, image in self.message_history:
            msg = ChatMessage(is_user)
            msg.setText(text)
            if image:
                msg.setImage(image)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, msg)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_history(self):
        """Clear the chat history."""
        while self.messages_layout.count() > 1:  # Keep the stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.message_history.clear()
    
    def restore_history(self):
        """Restore chat history from stored messages."""
        self.clear_history()
        for text, is_user in self.message_history:
            msg = ChatMessage(is_user)
            msg.setText(text)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, msg)

    def get_stylesheet(self):
        return """
            #chatWidget {
                background: #1e1e2e;
                border-radius: 8px;
            }
            #chatScroll {
                background: transparent;
                border: none;
            }
            #messagesContainer {
                background: transparent;
            }
            #inputContainer {
                background: #252535;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding: 0px;  # Removed padding completely
            }
            #followUpInput {
                background: #1e1e2e;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 5px;  /* Added minimal padding for better text positioning */
                margin: 0px;   /* Ensure no margin is affecting positioning */
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            #userMessage, #assistantMessage {
                background: #252535;
                border-radius: 8px;
                margin: 0px;
            }
            #userMessage {
                background: rgba(124, 124, 255, 0.1);
            }
            #messageContent {
                color: #ffffff;
                font-size: 13px;
                line-height: 1.5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            #roleIcon {
                color: #ffffff;
                font-size: 13px;
            }
            #roleLabel {
                color: #a0a0a0;
                font-size: 12px;
                font-weight: 500;
            }
            #copyButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.5);
                color: #7c7cff;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            #copyButton:hover {
                background: rgba(124, 124, 255, 0.1);
            }
            #sendButton {
                background: #7c7cff;
                border: none;
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                min-width: 70px;
                font-weight: 500;
                font-size: 12px;
            }
            #sendButton:hover {
                background: #6b6be5;
            }
        """

class FloatingDialog(QDialog):
    text_updated = pyqtSignal(str)
    follow_up_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Enable resizing
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
        self.setSizeGripEnabled(True)
        
        self.init_ui()
        self.setup_animations()
        
        self.text_updated.connect(self._update_streaming_text)
        self.current_text = ""
        self.current_assistant_message = None
        self.resize(800, 600)  # Set a larger default size
        self.normal_size = None  # Store normal size for minimize/restore
        self.is_minimized = False

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create main container with modern shadow effect
        self.container = QFrame()
        self.container.setObjectName("mainContainer")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Add title bar with modern icons
        self.title_bar = TitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Content area with improved spacing
        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Add thinking widget with modern styling
        self.thinking_widget = ThinkingWidget()
        content_layout.addWidget(self.thinking_widget)
        
        # Add chat widget with improved layout
        self.chat_widget = ChatWidget()
        content_layout.addWidget(self.chat_widget)
        
        # Add buttons layout
        self.button_layout = QHBoxLayout()
        content_layout.addLayout(self.button_layout)
        
        # Connect follow-up button
        self.chat_widget.send_btn.clicked.connect(self.handle_follow_up)
        
        content.setLayout(content_layout)
        container_layout.addWidget(content)
        
        self.container.setLayout(container_layout)
        layout.addWidget(self.container)
        self.setLayout(layout)

        # Set minimum size and make resizable
        self.setMinimumSize(500, 400)
        
        # Update styling
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        return """
            #mainContainer {
                background: #1e1e2e;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            #titleBar {
                background: #1e1e2e;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                min-height: 40px;
            }
            #titleLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            #minimizeBtn, #closeBtn {
                background: transparent;
                border: none;
                color: #ffffff;
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            #minimizeBtn:hover, #closeBtn:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            #content {
                background: #1e1e2e;
            }
            #thinkingWidget {
                background: #252535;
                border-radius: 8px;
                margin-bottom: 15px;
                padding: 12px;
            }
            #thinkingLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            #loadingDots {
                color: #7c7cff;
                font-size: 13px;
                font-weight: bold;
                min-width: 20px;
            }
            #toggleThinkingBtn {
                background: rgba(124, 124, 255, 0.1);
                border: none;
                color: #7c7cff;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
            }
            #toggleThinkingBtn:hover {
                background: rgba(124, 124, 255, 0.2);
            }
            #thinkingContent {
                background: #252535;
                color: #a0a0a0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                margin-top: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            #chatWidget {
                background: #252535;
                border-radius: 8px;
                padding: 15px;
            }
            #userMessage {
                background: rgba(124, 124, 255, 0.1);
                border-radius: 8px;
                margin: 8px 0;
                padding: 12px;
            }
            #assistantMessage {
                background: #252535;
                border-radius: 8px;
                margin: 8px 0;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            #messageContent {
                background: transparent;
                color: #ffffff;
                border: none;
                padding: 8px;
                font-size: 13px;
                line-height: 1.5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            #roleIcon {
                color: #ffffff;
                font-size: 13px;
            }
            #roleLabel {
                color: #a0a0a0;
                font-size: 12px;
                font-weight: 500;
            }
            #copyButton {
                background: transparent;
                border: 1px solid rgba(124, 124, 255, 0.5);
                color: #7c7cff;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            #copyButton:hover {
                background: rgba(124, 124, 255, 0.1);
            }
            #sendButton {
                background: #7c7cff;
                border: none;
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                min-width: 70px;
                font-weight: 500;
                font-size: 12px;
            }
            #sendButton:hover {
                background: #6b6be5;
            }
            #newChatBtn {
                background: transparent;
                border: 1px solid rgba(124, 124, 255, 0.5);
                color: #7c7cff;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            #newChatBtn:hover {
                background: rgba(124, 124, 255, 0.1);
            }
            QTextEdit {
                background: #252535;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                selection-background-color: rgba(124, 124, 255, 0.3);
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e2e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """

    def set_thinking_content(self, thinking_text: str):
        """Update thinking content."""
        pass

    def show_processing(self):
        """Show the dialog in processing state."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.thinking_widget.thinking_content.clear()
        self.thinking_widget.start_thinking()
        
        # Don't create an empty assistant message yet - we'll create it when we have content
        self.current_assistant_message = None
        
        # Show and position the dialog if not visible
        if not self.isVisible():
            self.position_on_screen()
            self.show()
            
        # Ensure dialog is visible and focused
        self.raise_()
        self.activateWindow()
        
        # Process events to ensure UI updates
        QApplication.processEvents()

    def update_streaming(self, text: str):
        """Update streaming text in the chat widget."""
        # Check if the text is an HTML message (contains image)
        if "<img" in text:
            # For image messages, create a new message immediately
            if self.current_assistant_message is None:
                self.chat_widget.add_message(text, is_user=True)
                self.current_assistant_message = None
                self.current_text = ""
            return
            
        # If we have an existing message, append to it
        if hasattr(self, 'current_assistant_message') and self.current_assistant_message:
            # Get current text and append new chunk
            current = self.current_assistant_message.content.text()
            updated_text = current + text
            
            # Update the message
            self.current_assistant_message.content.setText(updated_text)
            self.current_text = updated_text
        else:
            # Only create a new assistant message if we have actual content
            if text.strip():
                self.current_text = text
                self.current_assistant_message = self.chat_widget.add_message(text, is_user=False)
            else:
                # Just store the text without creating a message yet
                self.current_text = text
            
        # Process events to keep UI responsive without recursive repaints
        QApplication.processEvents()
        
        # Scroll to bottom without forcing a repaint
        self.chat_widget.scroll_to_bottom()

    def _update_streaming_text(self, new_text: str):
        """Update the text display with streaming content."""
        if not new_text.startswith("<think>"):
            # Remove leading/trailing whitespace only for the first chunk
            if not self.current_text:
                new_text = new_text.lstrip()
            self.current_text += new_text
            
            # Create assistant message if it doesn't exist yet and we have content
            if not self.current_assistant_message and self.current_text.strip():
                self.current_assistant_message = self.chat_widget.add_message("", is_user=False)
                
            if self.current_assistant_message:
                self.current_assistant_message.content.setText(self.current_text)
                self.chat_widget.scroll_to_bottom()
                # Process events to keep UI responsive
                QApplication.processEvents()

    def handle_follow_up(self):
        """Handle follow-up question submission."""
        text = self.chat_widget.follow_up_input.toPlainText().strip()
        if text:
            # Clear input first
            self.chat_widget.follow_up_input.clear()
            
            # Reset state for new response
            self.current_text = ""
            self.thinking_widget.thinking_content.clear()
            self.thinking_widget.start_thinking()
            
            # Add user message
            self.chat_widget.add_message(text, is_user=True)
            
            # Don't create an empty assistant message yet - we'll create it when we have content
            self.current_assistant_message = None
            
            # Ensure window is visible and scroll to bottom
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()
            self.chat_widget.scroll_to_bottom()
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
            # Emit the follow-up signal
            self.follow_up_submitted.emit(text)

    def set_thinking_content(self, text: str):
        """Set the thinking content."""
        if text.startswith("<think>") and text.endswith("</think>"):
            # Extract thinking content
            thinking_text = text[7:-8]  # Remove <think> and </think> tags
            self.thinking_widget.set_thinking(thinking_text)
            self.thinking_widget.thinking_label.setText("🤔 Thinking...")
        elif text.startswith("<think>"):
            # Start of thinking
            thinking_text = text[7:]  # Remove <think> tag
            self.thinking_widget.set_thinking(thinking_text)
            self.thinking_widget.thinking_label.setText("🤔 Thinking...")
        else:
            # Append to existing thinking content
            current = self.thinking_widget.thinking_content.toPlainText()
            self.thinking_widget.set_thinking(current + text)

    def position_on_screen(self):
        """Position the dialog in the bottom right corner of the screen."""
        # Get the primary screen using QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.adjustSize()
            
            # Position in bottom right with more padding
            x = screen_geometry.width() - self.width() - 50
            y = screen_geometry.height() - self.height() - 100
            self.move(x, y)
            
            # Ensure we're within screen bounds
            if x < 0:
                x = 50
            if y < 0:
                y = 50
            self.move(x, y)

    def setup_animations(self):
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade_out)
        self.opacity = 1.0

    def fade_out(self):
        """Gradually fade out the dialog."""
        self.opacity -= 0.1
        if self.opacity <= 0:
            self.fade_timer.stop()
            self.hide()
            self.opacity = 1.0
        else:
            self.setWindowOpacity(self.opacity)

    def auto_close(self, delay_ms: int = 5000):
        """Start auto-close timer."""
        self.fade_timer.start(100)  # Update every 100ms

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        # Update the size grip position
        if hasattr(self, 'container'):
            self.container.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, event):
        """Enable dragging and resizing."""
        if self.title_bar.geometry().contains(event.pos()):
            self.oldPos = event.globalPosition().toPoint()
        elif event.position().x() > self.width() - 20 and event.position().y() > self.height() - 20:
            # Bottom-right corner for resizing
            self.resizing = True
            self.oldPos = event.globalPosition().toPoint()
            self.oldSize = self.size()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle dragging and resizing."""
        if hasattr(self, 'oldPos'):
            delta = event.globalPosition().toPoint() - self.oldPos
            if hasattr(self, 'resizing') and self.resizing:
                # Handle resizing
                new_width = self.oldSize.width() + delta.x()
                new_height = self.oldSize.height() + delta.y()
                self.resize(max(self.minimumWidth(), new_width), 
                          max(self.minimumHeight(), new_height))
            else:
                # Handle dragging
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Handle end of dragging or resizing."""
        if hasattr(self, 'resizing'):
            self.resizing = False
        if hasattr(self, 'oldPos'):
            del self.oldPos
        if hasattr(self, 'oldSize'):
            del self.oldSize

    def showEvent(self, event):
        """Handle show events."""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Check if Enter was pressed in the follow-up input
        if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and \
           not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # Check if follow-up input has focus
            if self.chat_widget.follow_up_input.hasFocus():
                self.handle_follow_up()
                return
        
        super().keyPressEvent(event)

    def minimize(self):
        """Handle minimize button click."""
        if not self.is_minimized:
            # Store current size if not already minimized
            self.normal_size = self.size()
            # Shrink to a compact size
            self.resize(300, 40)
            self.is_minimized = True
        else:
            # Restore to normal size
            if self.normal_size:
                self.resize(self.normal_size)
            self.is_minimized = False
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Reset state but keep history
        self.current_text = ""
        self.current_assistant_message = None
        self.thinking_widget.thinking_content.clear()
        self.thinking_widget.thinking_label.setText("🤔 Thinking...")
        # Hide instead of close
        self.hide()
        event.ignore()

    def handle_processed_content(self, response: str):
        """Handle processed content from the AI."""
        self.thinking_widget.stop_thinking()

    def clear_chat(self):
        """Clear the chat history and reset the dialog."""
        # Clear chat history
        self.chat_widget.clear_history()
        
        # Reset current state
        self.current_text = ""
        self.current_assistant_message = None
        
        # Reset thinking widget
        self.thinking_widget.thinking_content.clear()
        self.thinking_widget.thinking_label.setText("🤔 Thinking")
        self.thinking_widget.thinking_icon.setText("🤔")
        self.thinking_widget.loading_dots.stop()
        
        # Clear follow-up input
        self.chat_widget.follow_up_input.clear()
        
        # Show a temporary welcome message
        welcome_msg = self.chat_widget.add_message(
            "Start a new conversation by copying text or using Ctrl + Shift + U",
            is_user=False
        )
