from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QByteArray, QBuffer, QThread, Qt
from PyQt6.QtGui import QClipboard, QImage
import pyperclip
import io
import base64
from typing import Optional, Union, Generator
from .config import config
from .ollama_integration import ollama
from .image_worker import ImageWorker
from PyQt6.QtWidgets import QApplication

class ClipboardMonitor(QObject):
    content_processed = pyqtSignal(str)  # Signal emitted when content is processed
    error_occurred = pyqtSignal(str)     # Signal emitted when an error occurs
    processing_started = pyqtSignal()    # Signal emitted when processing starts
    stream_received = pyqtSignal(str)    # Signal emitted when stream chunk received
    thinking_update = pyqtSignal(str)
    notes_requested = pyqtSignal()  # Signal to request notes from user
    image_detected = pyqtSignal(QImage)  # Signal emitted when an image is detected in clipboard
    image_progress = pyqtSignal(int)  # Signal emitted to report image processing progress
    image_processed_signal = pyqtSignal(str, QImage)  # Signal emitted when image processing is complete

    def __init__(self, clipboard: QClipboard):
        super().__init__()
        # Ensure we're on the main thread
        if QThread.currentThread() != QApplication.instance().thread():
            raise RuntimeError("ClipboardMonitor must be created on the main thread")
            
        self.clipboard = clipboard
        self.paused = False
        self.last_text = ""
        self.current_context = []
        self.last_copied_text = None
        self.last_copied_image = None
        self.processing_lock = False
        self.clipboard_retry_count = 0
        self.MAX_RETRIES = 3
        
        # Connect to clipboard changes on the main thread
        QTimer.singleShot(0, lambda: self.clipboard.dataChanged.connect(self._on_clipboard_change))
        
        # Create timer on the main thread
        self.check_timer = QTimer()
        self.check_timer.moveToThread(QApplication.instance().thread())
        self.check_timer.timeout.connect(self._check_clipboard)
        # Start timer on the main thread
        QTimer.singleShot(0, lambda: self.check_timer.start(1000))  # Check every second

    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content with retry mechanism."""
        self.clipboard_retry_count = 0
        while self.clipboard_retry_count < self.MAX_RETRIES:
            try:
                mime_data = self.clipboard.mimeData()
                if mime_data and mime_data.hasText():
                    text = mime_data.text()
                    if text:
                        return text.strip()
                # If no text found, try again after a short delay
                QApplication.processEvents()
                QTimer.singleShot(100, lambda: None)
                self.clipboard_retry_count += 1
            except Exception as e:
                self.error_occurred.emit(f"Error reading clipboard (attempt {self.clipboard_retry_count + 1}): {str(e)}")
                self.clipboard_retry_count += 1
        return None

    def _store_clipboard_content(self):
        """Safely store clipboard content."""
        if self.processing_lock:
            return
            
        try:
            # First try to get selected text
            selected_text = None
            try:
                selected_text = self.clipboard.text(QClipboard.Mode.Selection)
                if selected_text:
                    selected_text = selected_text.strip()
            except:
                pass
                
            # If no selected text, try clipboard text
            if not selected_text:
                clipboard_text = self._get_clipboard_content()
                if clipboard_text:
                    self.last_copied_text = clipboard_text
                    return True
            else:
                self.last_copied_text = selected_text
                return True
                
        except Exception as e:
            self.error_occurred.emit(f"Error storing clipboard content: {str(e)}")
            
        return False

    def _on_clipboard_change(self):
        """Handle clipboard content changes."""
        if not self.paused and not self.processing_lock:
            # First check for image content
            if self._check_for_image():
                # If in auto mode, process the image immediately
                if config.get("processing_mode") == "auto":
                    self.image_detected.emit(self.last_copied_image)
                return
                
            # Then check for text content
            success = self._store_clipboard_content()
            if success and config.get("processing_mode") == "auto":
                self._process_current_content()

    def _check_clipboard(self):
        """Periodic clipboard check as a fallback."""
        if not self.paused and config.get("processing_mode") == "auto":
            # First check for image content
            if self._check_for_image():
                self.image_detected.emit(self.last_copied_image)
                return
                
            # Then check for text content
            current_content = self._get_clipboard_content()
            if current_content and current_content != self.last_text:
                self._process_current_content()

    def _handle_stream(self, text: str):
        """Handle streaming text from Ollama."""
        self.stream_received.emit(text)

    def _process_current_content(self) -> None:
        """Process the current clipboard content."""
        content = self._get_clipboard_content()
        if not content or content == self.last_text:
            return

        self.last_text = content
        
        try:
            # Emit processing started signal
            self.processing_started.emit()
            
            # Process with Ollama using streaming
            response = ollama.generate_response(
                content,
                on_stream=self._handle_stream
            )
            self.content_processed.emit(response)
        except Exception as e:
            self.error_occurred.emit(f"Error processing content: {str(e)}")

    def process_on_demand(self) -> None:
        """Process clipboard content on demand."""
        if self.paused:
            return

        try:
            # First check for image content
            if self._check_for_image():
                self.image_detected.emit(self.last_copied_image)
                return
                
            # Then check for text content
            # First check for selected text
            selected_text = None
            copied_text = None
            
            # Try to get selected text
            try:
                selected_text = self.clipboard.text(QClipboard.Mode.Selection)
                if selected_text:
                    selected_text = selected_text.strip()
            except:
                pass
            
            # If no selected text, try to get copied text
            if not selected_text:
                mime = self.clipboard.mimeData()
                if mime and mime.hasText():
                    copied_text = mime.text().strip()
            
            # Store the text but don't process yet - wait for notes
            text_to_store = selected_text or copied_text
            if text_to_store:
                self.last_copied_text = text_to_store
                # Request notes first
                self.request_notes()
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
        except Exception as e:
            self.error_occurred.emit(f"Error in process_on_demand: {str(e)}")
            QApplication.processEvents()

    def process_text(self, text: str, is_follow_up: bool = False):
        """Process text content."""
        try:
            # Emit processing started signal
            self.processing_started.emit()
            
            # Prepare prompt based on whether it's a follow-up
            if is_follow_up and self.current_context:
                # Build context from previous conversation
                context = "\n".join([
                    f"{'User' if role == 'user' else 'Assistant'}: {content}"
                    for content, role in self.current_context
                ])
                prompt = f"{context}\n\nUser: {text}\n\nAssistant: Let me help you with that follow-up question."
            else:
                prompt = text
            
            response_text = ""
            thinking_text = ""
            in_thinking = False
            
            # Get model response with streaming
            try:
                for chunk in ollama.generate_stream(prompt):
                    # Process events periodically to prevent UI freezing
                    QApplication.processEvents()
                    
                    if chunk.startswith("<think>"):
                        in_thinking = True
                        thinking_text = chunk[7:]  # Remove <think> prefix
                        self.thinking_update.emit(chunk)
                    elif chunk.endswith("</think>"):
                        in_thinking = False
                        thinking_text += chunk[:-8]  # Remove </think> suffix
                        self.thinking_update.emit("<think>" + thinking_text + "</think>")
                    else:
                        if in_thinking:
                            thinking_text += chunk
                            self.thinking_update.emit("<think>" + thinking_text + "</think>")
                        else:
                            response_text += chunk
                            self.stream_received.emit(chunk)
                    
                    # Process events after each chunk
                    QApplication.processEvents()
                
                # Add response to context
                self.current_context.append((response_text, "assistant"))
                
                # Emit completion signal
                self.content_processed.emit("complete")
                
            except Exception as e:
                self.error_occurred.emit(f"Error during streaming: {str(e)}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error processing text: {str(e)}")
            
        # Process events one final time
        QApplication.processEvents()

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """Generate streaming response using Ollama."""
        try:
            for chunk in ollama.generate_stream(prompt):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    def process_follow_up(self, question: str):
        """Process a follow-up question."""
        if self.paused or not question.strip():
            return

        try:
            self.current_context.append((question, "user"))
            # Process events before starting
            QApplication.processEvents()
            self.process_text(question, is_follow_up=True)
        except Exception as e:
            self.error_occurred.emit(f"Error processing follow-up: {str(e)}")

    def process_image(self, image: QImage, notes: str = None):
        """Process image content with optional notes."""
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
            
        try:
            self.processing_lock = True
            
            # First, emit the user message with image and notes to show in the chat
            user_message = "[Image Analysis Request]\n"
            if notes:
                user_message += f"Question: {notes}\n"
            user_message += "[Attached Image]"
            
            # Add to context before processing
            self.current_context.append((user_message, "user"))
            
            # Emit the user message to display in the chat immediately
            # This will trigger the UI to show the user's message with the image
            self.image_processed_signal.emit("", image)  # Empty response, just to display the image
            
            # Emit processing started signal
            self.processing_started.emit()
            
            # Create worker thread
            self.worker_thread = QThread()
            self.worker = ImageWorker(image, notes)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker_thread.started.connect(self.worker.process)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.response_ready.connect(lambda response: self._handle_image_response(response, image, notes))
            self.worker.error.connect(lambda e: self.error_occurred.emit(f"Error processing image: {e}"))
            self.worker.progress.connect(self.image_progress.emit)
            
            # Connect stream chunk signal to handle streaming updates
            self.worker.stream_chunk.connect(self._handle_stream)
            
            # Report initial progress
            self.image_progress.emit(0)
            
            # Start processing
            self.worker_thread.start()
            
        except Exception as e:
            self.error_occurred.emit(f"Error setting up image processing: {str(e)}")
            self.processing_lock = False
            # Convert QImage to bytes using QByteArray
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            image_data = byte_array.data()
            
            # Create a scaled version of the image for display
            scaled_image = image.scaled(
                400, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create HTML for displaying the image in the chat
            image_html = f'<img src="data:image/png;base64,{base64.b64encode(image_data).decode("utf-8")}" width="400" style="max-width: 100%; border-radius: 8px;">' 
            
            # Add user message with image and notes
            message = f"{image_html}<br><br>My question: {notes if notes else 'Please analyze this image.'}"
            self.content_processed.emit(message)
            
            # Create prompt for the model
            prompt = f"[Image: data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}] {notes if notes else 'Please analyze this image and describe what you see.'}"
            
            # Process in a separate thread
            def process_in_thread():
                try:
                    response = ollama.generate_response(prompt)
                    # Add both the image and response to context
                    self.current_context.append((message, "user"))
                    self.current_context.append((response, "assistant"))
                    # Emit the complete response
                    self.content_processed.emit(response)
                except Exception as e:
                    self.error_occurred.emit(f"Error processing image: {str(e)}")
                finally:
                    self.processing_lock = False
            
            # Create and start the thread
            thread = QThread()
            worker = QObject()
            worker.moveToThread(thread)
            thread.started.connect(process_in_thread)
            thread.start()
            
        except Exception as e:
            self.error_occurred.emit(f"Error preparing image: {str(e)}")
            self.processing_lock = False
            # Encode image data to base64
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            
            # Create prompt based on whether notes were provided
            if notes:
                prompt = f"[Image: data:image/png;base64,{encoded_image}] Please analyze this image with the following instructions: {notes}"
            else:
                prompt = f"[Image: data:image/png;base64,{encoded_image}] Please analyze this image and describe what you see."
            
            # Process events before model call
            QApplication.processEvents()
            
            # Get model response without streaming for vision model
            response = ollama.generate_response(prompt)
            
            # Process events after getting response
            QApplication.processEvents()
            
            # Add both the image and response to context
            self.current_context.append((f"[Image Analysis Request] {notes if notes else 'Please analyze this image.'}\n[Attached Image]", "user"))
            self.current_context.append((response, "assistant"))
            
            # Process events before emitting response
            QApplication.processEvents()
            
            # Emit the complete response
            self.content_processed.emit(response)
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing image: {str(e)}")
        finally:
            # Clean up and release processing lock
            self.processing_lock = False
            # Process events one final time
            QApplication.processEvents()

    def toggle_pause(self) -> bool:
        """Toggle the pause state of the monitor."""
        self.paused = not self.paused
        return self.paused

    def set_paused(self, paused: bool) -> None:
        """Set the paused state of the monitor."""
        self.paused = paused

    def process_with_notes(self, notes: str):
        """Process the last copied text with additional notes."""
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
            
        if not self.last_copied_text:
            self.error_occurred.emit("No content found to process with notes")
            return
            
        try:
            self.processing_lock = True
            
            # Create a structured prompt that clearly separates content and notes
            combined_text = (
                "Please analyze the following content based on my notes/questions:\n\n"
                "=== MY NOTES/QUESTIONS ===\n"
                f"{notes}\n\n"
                "=== CONTENT TO ANALYZE ===\n"
                f"{self.last_copied_text}\n\n"
                "Please address my notes/questions in relation to the content above."
            )
            
            self.current_context = [(combined_text, "user")]
            self.process_text(combined_text)
            
            # Clear the stored text after processing
            self.last_copied_text = None
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing with notes: {str(e)}")
        finally:
            self.processing_lock = False

    def request_notes(self):
        """Request notes from user for the last copied text."""
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
            
        if not self._store_clipboard_content():
            self.error_occurred.emit("Could not access clipboard content")
            return
            
        if not self.last_copied_text:
            self.error_occurred.emit("No recent text found to add notes to")
            return
            
        self.notes_requested.emit()
        
    def _check_for_image(self) -> bool:
        """Check if clipboard contains an image and store it if found."""
        if self.processing_lock:
            return False
            
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Process events to keep UI responsive
                QApplication.processEvents()
                
                # Add a longer delay between retries and process events
                if retry_count > 0:
                    QTimer.singleShot(250, lambda: None)
                    QApplication.processEvents()
                
                mime_data = self.clipboard.mimeData()
                if mime_data and mime_data.hasImage():
                    # Get the image data directly from mime data
                    image = mime_data.imageData()
                    if image and not image.isNull():
                        self.last_copied_image = image
                        return True
                    # Fallback to clipboard image if mime data image is null
                    image = QImage(self.clipboard.image())
                    if not image.isNull():
                        self.last_copied_image = image
                        return True
                        
                retry_count += 1
            except Exception as e:
                self.error_occurred.emit(f"Error checking for image (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                
        return False
        
    def process_image_with_notes(self, notes: str):
        """Process the last copied image with additional notes."""
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
            
        if not self.last_copied_image:
            self.error_occurred.emit("No image found to process with notes")
            return
            
        try:
            self.processing_lock = True
            
            # Process the image with the provided notes
            self.process_image(self.last_copied_image, notes)
            
            # Clear the stored image after processing
            self.last_copied_image = None
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing image with notes: {str(e)}")
        finally:
            self.processing_lock = False

    def _handle_image_response(self, response: str, image: QImage = None, notes: str = None):
        """Handle the response from image processing."""
        try:
            # Add both the image and response to context with notes
            user_message = "[Image Analysis Request]\n"
            if notes:
                user_message += f"Question: {notes}\n"
            user_message += "[Attached Image]"
            
            self.current_context.append((user_message, "user"))
            self.current_context.append((response, "assistant"))
            
            # Emit the complete response with the image
            self.content_processed.emit(response)
            
            # Store the image for display in the UI
            if image:
                # Create a deep copy of the image to avoid thread issues
                display_image = QImage(image)
                # Emit a special signal with both the response and image
                self.image_processed_signal.emit(response, display_image)
        except Exception as e:
            self.error_occurred.emit(f"Error handling image response: {str(e)}")
        finally:
            self.processing_lock = False
            
    def _cleanup_previous_image_processing(self):
        """Clean up any ongoing image processing."""
        try:
            # Stop any worker threads that might be running
            if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(1000)  # Wait up to 1 second for thread to finish
                
            # Release processing lock if it's set
            self.processing_lock = False
        except Exception as e:
            print(f"Error cleaning up image processing: {str(e)}")
