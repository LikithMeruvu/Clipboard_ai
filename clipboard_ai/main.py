import sys
import signal
from PyQt6.QtCore import QObject, QThread, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QClipboard, QImage
from .ui.tray import SystemTray
from .ui.floating_dialog import FloatingDialog
from .clipboard_monitor import ClipboardMonitor
from .hotkey_manager import HotkeyManager
from .config import config
from .ollama_integration import ollama
from .ui.notes_dialog import NotesDialog
from .ui.image_dialog import ImageDialog
import gc

class ClipboardAI(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.clipboard = QApplication.clipboard()
        
        # Initialize components
        self.init_components()
        
        # Set up signal handling for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def init_components(self):
        """Initialize all application components."""
        # Check Ollama availability
        if not ollama.check_ollama_status():
            print("Error: Ollama is not running or not accessible.")
            print("Please make sure Ollama is installed and running.")
            sys.exit(1)

        # Ensure we're on the main thread
        if QThread.currentThread() != QApplication.instance().thread():
            raise RuntimeError("Components must be initialized on the main thread")

        # Initialize floating dialog
        self.floating_dialog = FloatingDialog()
        self.floating_dialog.follow_up_submitted.connect(self.handle_follow_up)
        # Connect clear_chat signal to handle_clear_chat method
        self.floating_dialog.title_bar.new_chat_btn.clicked.disconnect()
        self.floating_dialog.title_bar.new_chat_btn.clicked.connect(self.handle_clear_chat)
        self.floating_dialog.hide()  # Ensure it starts hidden

        # Initialize system tray
        self.tray = SystemTray(self.app)
        self.tray.set_pause_callback(self.handle_pause)
        self.tray.set_mode_change_callback(self.handle_mode_change)

        # Initialize clipboard monitor
        self.clipboard_monitor = ClipboardMonitor(self.clipboard)
        self.clipboard_monitor.moveToThread(QApplication.instance().thread())
        self.clipboard_monitor.content_processed.connect(self.handle_processed_content)
        self.clipboard_monitor.error_occurred.connect(self.handle_error)
        self.clipboard_monitor.processing_started.connect(self.handle_processing_started)
        self.clipboard_monitor.stream_received.connect(self.handle_stream_update)
        self.clipboard_monitor.thinking_update.connect(self.handle_thinking_update)
        self.clipboard_monitor.notes_requested.connect(self.handle_notes_request)
        self.clipboard_monitor.image_detected.connect(self.handle_image_detected)
        self.clipboard_monitor.image_progress.connect(self.handle_image_progress)
        self.clipboard_monitor.image_processed_signal.connect(self.handle_image_processed)

        # Initialize hotkey managers in the main thread
        self.hotkey = HotkeyManager()
        self.hotkey.register_hotkey(self.handle_hotkey)
        
        # Register notes hotkey
        self.notes_hotkey = HotkeyManager()
        self.notes_hotkey.register_hotkey(
            self.handle_notes_hotkey,
            config.get("notes_hotkey")
        )
        
        # Register image hotkey
        self.image_hotkey = HotkeyManager()
        self.image_hotkey.register_hotkey(
            self.handle_image_hotkey,
            "ctrl+shift+o"
        )

    def handle_processing_started(self):
        """Handle when processing starts."""
        self.floating_dialog.show_processing()
        self.floating_dialog.raise_()
        self.floating_dialog.activateWindow()

    def handle_stream_update(self, text: str):
        """Handle streaming updates from the AI."""
        self.floating_dialog.update_streaming(text)

    def handle_thinking_update(self, text: str):
        """Handle thinking updates from the AI."""
        self.floating_dialog.set_thinking_content(text)
        
    def handle_image_progress(self, progress: int):
        """Handle image processing progress updates."""
        # Update the thinking widget with progress information
        if progress < 100:
            self.floating_dialog.thinking_widget.thinking_label.setText(f"⏳ Processing image... {progress}%")
        else:
            self.floating_dialog.thinking_widget.thinking_label.setText("✓ Image processed")

    def handle_processed_content(self, response: str):
        """Handle processed content from the AI."""
        # Update status only
        self.floating_dialog.thinking_widget.thinking_label.setText("✓ Complete")

    def handle_follow_up(self, question: str):
        """Handle follow-up questions."""
        self.clipboard_monitor.process_follow_up(question)

    def handle_error(self, error_message: str):
        """Handle errors from components."""
        # Show the dialog if not visible
        if not self.floating_dialog.isVisible():
            self.floating_dialog.show_processing()
        
        # Add error message as an assistant message
        self.floating_dialog.chat_widget.add_message(f"Error: {error_message}", is_user=False)
        
        # Update thinking widget to show error state
        self.floating_dialog.thinking_widget.thinking_label.setText("❌ Error")
        
        # Ensure dialog is visible
        self.floating_dialog.raise_()
        self.floating_dialog.activateWindow()

    def handle_pause(self, is_paused: bool):
        """Handle pause/resume events."""
        self.clipboard_monitor.set_paused(is_paused)
        status = "paused" if is_paused else "resumed"
        self.tray.show_notification(
            "Status Change",
            f"Clipboard monitoring {status}"
        )

    def handle_mode_change(self, mode: str):
        """Handle processing mode changes."""
        self.tray.show_notification(
            "Mode Change",
            f"Switched to {mode} processing mode"
        )

    def handle_hotkey(self):
        """Handle hotkey press events."""
        if config.get("processing_mode") == "manual":
            self.clipboard_monitor.process_on_demand()

    def handle_notes_hotkey(self):
        """Handle notes hotkey press."""
        if not self.clipboard_monitor.paused:
            self.clipboard_monitor.request_notes()
            
    def handle_image_hotkey(self):
        """Handle image hotkey press."""
        if not self.clipboard_monitor.paused:
            # Process events before checking clipboard
            QApplication.processEvents()
            
            # Add a small delay to ensure clipboard is accessible
            QTimer.singleShot(100, self._process_image_hotkey)
    
    def _process_image_hotkey(self):
        """Process the image hotkey after delay."""
        try:
            # Check if there's an image in the clipboard
            if self.clipboard_monitor._check_for_image():
                # Create a deep copy of the image to avoid thread issues
                image_copy = QImage(self.clipboard_monitor.last_copied_image)
                self.handle_image_detected(image_copy)
            else:
                self.handle_error("No image found in clipboard")
        except Exception as e:
            self.handle_error(f"Error processing image hotkey: {str(e)}")
                
    def handle_image_detected(self, image: QImage):
        """Handle when an image is detected in the clipboard."""
        def show_dialog():
            try:
                # Create a deep copy of the image for the dialog
                dialog_image = QImage(image)
                dialog = ImageDialog(dialog_image, self.floating_dialog)
                
                # Connect the notes_submitted signal to process the image
                dialog.notes_submitted.connect(lambda notes: 
                    self.clipboard_monitor.process_image(dialog_image, notes))
                
                dialog.show()
                dialog.raise_()
                dialog.activateWindow()
            except Exception as e:
                self.handle_error(f"Error showing image dialog: {str(e)}")
        
        # Ensure dialog is created and shown on the main thread
        QTimer.singleShot(0, show_dialog)

    def handle_notes_request(self):
        """Handle request for notes input."""
        if not self.clipboard_monitor.last_copied_text:
            self.floating_dialog.error_occurred.emit("No recent text found to add notes to")
            return
            
        # Create and show the notes dialog
        notes_dialog = NotesDialog(self.clipboard_monitor.last_copied_text)
        notes_dialog.notes_submitted.connect(self.handle_notes_submit)
        notes_dialog.exec()  # Modal dialog

    def handle_notes_submit(self, notes: str):
        """Handle submitted notes."""
        try:
            # Get the copied text before showing any dialogs
            copied_text = self.clipboard_monitor.last_copied_text
            
            # Prepare the combined message
            combined_message = (
                f"Content: {copied_text}\n\n"
                f"My Notes/Questions: {notes}"
            )
            
            # Clear and prepare the floating dialog first
            self.floating_dialog.clear_chat()
            
            # Add the user message
            self.floating_dialog.chat_widget.add_message(combined_message, is_user=True)
            
            # Process the combined message
            self.clipboard_monitor.process_with_notes(notes)
            
        except Exception as e:
            self.handle_error(f"Error processing notes: {str(e)}")

    def handle_image_processed(self, response: str, image: QImage):
        """Handle when an image has been processed with its response."""
        try:
            # Get the notes if they were provided
            notes = ""
            for content, role in self.clipboard_monitor.current_context:
                if role == "user" and "[Image Analysis Request]" in content and "Question:" in content:
                    # Extract the notes from the user message
                    start_idx = content.find("Question:") + 10
                    end_idx = content.find("\n[Attached Image]")
                    if end_idx > start_idx:
                        notes = content[start_idx:end_idx].strip()
                    break
            
            # If response is empty, this is just the initial display of the user's message
            if not response:
                # Add the user's image message with notes first
                user_message = "[Image Analysis Request]"
                if notes:
                    user_message += f"\nQuestion: {notes}"
                user_message += "\n[Attached Image]"
                
                self.floating_dialog.chat_widget.add_message(user_message, is_user=True, image=image)
                
                # Don't create an empty assistant message yet - we'll create it when we have content
                self.floating_dialog.current_assistant_message = None
                
                # Update status to show processing
                self.floating_dialog.thinking_widget.thinking_label.setText("⏳ Processing image... 0%")
                
                # Ensure dialog is visible and focused
                self.floating_dialog.show()
                self.floating_dialog.raise_()
                self.floating_dialog.activateWindow()
                
                # Scroll to bottom to show the response
                self.floating_dialog.chat_widget.scroll_to_bottom()
            else:
                # This is the final response, update the assistant's message
                # Update status
                self.floating_dialog.thinking_widget.thinking_label.setText("✓ Complete")
                
                # If we have a current assistant message, update it
                if hasattr(self.floating_dialog, 'current_assistant_message') and self.floating_dialog.current_assistant_message:
                    self.floating_dialog.current_assistant_message.setText(response)
                else:
                    # Otherwise create a new one
                    self.floating_dialog.chat_widget.add_message(response, is_user=False)
                
                # Ensure dialog is visible and focused
                self.floating_dialog.show()
                self.floating_dialog.raise_()
                self.floating_dialog.activateWindow()
                
                # Scroll to bottom to show the response
                self.floating_dialog.chat_widget.scroll_to_bottom()
        except Exception as e:
            self.handle_error(f"Error displaying image response: {str(e)}")

    def handle_clear_chat(self):
        """Handle clearing the chat and resetting the state."""
        # First clear the clipboard monitor context to stop any ongoing processing
        self.clipboard_monitor.clear_context()
        
        # Then clear the UI
        self.floating_dialog.clear_chat()
        
        # Instead of hiding, ensure the dialog remains visible
        # This prevents the window from closing unexpectedly
        self.floating_dialog.show()
        self.floating_dialog.raise_()
        self.floating_dialog.activateWindow()

    def signal_handler(self, sig, frame):
        """Handle system signals for clean shutdown."""
        print("\nShutting down gracefully...")
        # Clean up resources
        self._cleanup_resources()
        sys.exit(0)
        
    def _cleanup_resources(self):
        """Clean up resources before shutdown."""
        try:
            # Stop any ongoing image processing
            if hasattr(self, 'clipboard_monitor') and self.clipboard_monitor:
                self.clipboard_monitor._cleanup_previous_image_processing()
                
            # Force garbage collection
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def _run_application(self):
        """Internal method to run the application with exception handling."""
        try:
            # Set up exception hook to catch unhandled exceptions
            sys.excepthook = self._exception_hook
            
            # Run the application
            exit_code = self.app.exec()
            
            # Clean up resources before exit
            self._cleanup_resources()
            
            return exit_code
        except Exception as e:
            print(f"Error running application: {str(e)}")
            return 1
            
    def _exception_hook(self, exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions."""
        print(f"Unhandled exception: {exc_value}")
        # Clean up resources
        self.cleanup()
        # Call the default exception hook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def cleanup(self):
        """Clean up resources before shutdown."""
        self.hotkey.unregister_hotkey()
        self.notes_hotkey.unregister_hotkey()
        self.image_hotkey.unregister_hotkey()

    def run(self):
        """Start the application."""
        # Show initial notification
        self.tray.show_notification(
            "Clipboard AI",
            f"Using model: {config.get('selected_model')}\n"
            f"Mode: {config.get('processing_mode')}\n"
            f"Hotkey: {config.get('hotkey')}"
        )
        
        try:
            # Set up exception hook to catch unhandled exceptions
            sys.excepthook = self._exception_hook
            
            # Start the application
            exit_code = self.app.exec()
            
            # Clean up resources before exit
            self.cleanup()
            
            sys.exit(exit_code)
        except Exception as e:
            print(f"Error running application: {str(e)}")
            self.cleanup()
            sys.exit(1)

def main():
    """Application entry point."""
    app = ClipboardAI()
    app.run()

if __name__ == "__main__":
    main()
