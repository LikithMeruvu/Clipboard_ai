# clipboard_ai/clipboard_monitor.py
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, Qt
from PyQt6.QtGui import QClipboard, QImage
from PyQt6.QtWidgets import QApplication
import pyperclip
import io
import base64
from typing import Optional, Generator
from .config import config
from .ollama_integration import ollama
from .image_worker import ImageWorker

# Import the TextWorker class for offloading text processing
from .text_worker import TextWorker

class ClipboardMonitor(QObject):
    content_processed = pyqtSignal(str)  # Signal emitted when content is processed
    error_occurred = pyqtSignal(str)     # Signal emitted when an error occurs
    processing_started = pyqtSignal()    # Signal emitted when processing starts
    stream_received = pyqtSignal(str)    # Signal emitted when stream chunk received
    thinking_update = pyqtSignal(str)
    notes_requested = pyqtSignal()         # Signal to request notes from user
    image_detected = pyqtSignal(QImage)     # Signal emitted when an image is detected in clipboard
    image_progress = pyqtSignal(int)       # Signal emitted to report image processing progress
    image_processed_signal = pyqtSignal(str, QImage)  # Signal emitted when image processing is complete

    def __init__(self, clipboard: QClipboard):
        super().__init__()
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
        self.last_request_type = None
        
        QTimer.singleShot(0, lambda: self.clipboard.dataChanged.connect(self._on_clipboard_change))
        
        self.check_timer = QTimer()
        self.check_timer.moveToThread(QApplication.instance().thread())
        self.check_timer.timeout.connect(self._check_clipboard)
        QTimer.singleShot(0, lambda: self.check_timer.start(1000))  # Check every second

    def _get_clipboard_content(self) -> Optional[str]:
        self.clipboard_retry_count = 0
        while self.clipboard_retry_count < self.MAX_RETRIES:
            try:
                mime_data = self.clipboard.mimeData()
                if mime_data and mime_data.hasText():
                    text = mime_data.text()
                    if text:
                        return text.strip()
                QApplication.processEvents()
                QTimer.singleShot(100, lambda: None)
                self.clipboard_retry_count += 1
            except Exception as e:
                self.error_occurred.emit(f"Error reading clipboard (attempt {self.clipboard_retry_count + 1}): {str(e)}")
                self.clipboard_retry_count += 1
        return None

    def _store_clipboard_content(self):
        if self.processing_lock:
            return
        try:
            selected_text = None
            try:
                selected_text = self.clipboard.text(QClipboard.Mode.Selection)
                if selected_text:
                    selected_text = selected_text.strip()
            except:
                pass
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
        if not self.paused and not self.processing_lock:
            if self._check_for_image():
                if config.get("processing_mode") == "auto":
                    self.image_detected.emit(self.last_copied_image)
                return
            success = self._store_clipboard_content()
            if success and config.get("processing_mode") == "auto":
                self._process_current_content()

    def _check_clipboard(self):
        if not self.paused and config.get("processing_mode") == "auto":
            if self._check_for_image():
                self.image_detected.emit(self.last_copied_image)
                return
            current_content = self._get_clipboard_content()
            if current_content and current_content != self.last_text:
                self._process_current_content()

    def _handle_stream(self, text: str):
        self.stream_received.emit(text)

    def _process_current_content(self) -> None:
        content = self._get_clipboard_content()
        if not content or content == self.last_text:
            return
        self.last_text = content
        
        self.processing_started.emit()
        # Offload text processing to a worker thread
        self.text_thread = QThread()
        self.text_worker = TextWorker(prompt=content)
        self.text_worker.moveToThread(self.text_thread)
        self.text_thread.started.connect(self.text_worker.process)
        self.text_worker.result_ready.connect(lambda result: self.content_processed.emit(result))
        self.text_worker.stream_chunk.connect(self._handle_stream)
        self.text_worker.error.connect(lambda err: self.error_occurred.emit(f"Error processing content: {err}"))
        self.text_worker.finished.connect(self.text_thread.quit)
        self.text_worker.finished.connect(self.text_worker.deleteLater)
        self.text_thread.finished.connect(self.text_thread.deleteLater)
        self.text_thread.start()

    def process_on_demand(self) -> None:
        if self.paused:
            return
        try:
            if self._check_for_image():
                self.image_detected.emit(self.last_copied_image)
                return
            selected_text = None
            copied_text = None
            try:
                selected_text = self.clipboard.text(QClipboard.Mode.Selection)
                if selected_text:
                    selected_text = selected_text.strip()
            except:
                pass
            if not selected_text:
                mime = self.clipboard.mimeData()
                if mime and mime.hasText():
                    copied_text = mime.text().strip()
            text_to_store = selected_text or copied_text
            if text_to_store:
                self.last_copied_text = text_to_store
                self.request_notes()
            QApplication.processEvents()
        except Exception as e:
            self.error_occurred.emit(f"Error in process_on_demand: {str(e)}")
            QApplication.processEvents()

    def clear_context(self):
        print("Clearing conversation context and state")
        # First clear data
        self.current_context.clear()
        self.last_copied_text = None
        self.last_copied_image = None
        self.last_text = ""
        self.last_request_type = None
        
        # Ensure we're not in a locked state
        self.processing_lock = False
        
        # Stop any ongoing image processing
        self._cleanup_previous_image_processing()
        
        # If there's an active text processing thread, stop it properly
        if hasattr(self, 'text_thread') and self.text_thread and self.text_thread.isRunning():
            try:
                # Disconnect any signals to prevent callbacks during shutdown
                if hasattr(self, 'text_worker') and self.text_worker:
                    try:
                        self.text_worker.result_ready.disconnect()
                        self.text_worker.stream_chunk.disconnect()
                        self.text_worker.error.disconnect()
                        self.text_worker.finished.disconnect()
                    except Exception:
                        pass  # Ignore if already disconnected
                
                # Request the thread to quit and wait longer for it to finish
                self.text_thread.quit()
                if not self.text_thread.wait(2000):  # Wait up to 2 seconds
                    print("Text thread did not terminate gracefully, forcing termination")
                    self.text_thread.terminate()
                    self.text_thread.wait(1000)  # Give it another second
            except Exception as e:
                print(f"Error cleaning up text thread: {str(e)}")
        
        # Process events to ensure UI remains responsive
        QApplication.processEvents()

    def process_text(self, text: str, is_follow_up: bool = False):
        try:
            self.processing_started.emit()
            self.text_thread = QThread()
            self.text_worker = TextWorker(prompt=text, is_follow_up=is_follow_up, context=self.current_context)
            self.text_worker.moveToThread(self.text_thread)
            self.text_thread.started.connect(self.text_worker.process)
            self.text_worker.result_ready.connect(lambda result: self._handle_text_result(result))
            self.text_worker.stream_chunk.connect(self._handle_stream)
            self.text_worker.error.connect(lambda err: self.error_occurred.emit(f"Error processing text: {err}"))
            self.text_worker.finished.connect(self.text_thread.quit)
            self.text_worker.finished.connect(self.text_worker.deleteLater)
            self.text_thread.finished.connect(self.text_thread.deleteLater)
            self.text_thread.start()
            self.last_request_type = "text"  # Set the request type for text processing
        except Exception as e:
            self.error_occurred.emit(f"Error processing text: {str(e)}")

    def _handle_text_result(self, result: str):
        self.current_context.append((result, "assistant"))
        self.content_processed.emit("complete")

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        try:
            for chunk in ollama.generate_stream(prompt):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    def process_follow_up(self, question: str):
        if self.paused or not question.strip():
            return
        try:
            self.current_context.append((question, "user"))
            QApplication.processEvents()
            if self.last_request_type == "image" and self.last_copied_image is not None:
                print("Processing follow-up for image")
                self.process_image(self.last_copied_image, notes=question)
            elif self.last_request_type == "text":
                print("Processing follow-up for text")
                self.process_text(question, is_follow_up=True)
            else:
                self.error_occurred.emit("No previous context found for follow-up")
                return
        except Exception as e:
            self.error_occurred.emit(f"Error processing follow-up: {str(e)}")

    def process_image(self, image: QImage, notes: str = None):
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
        try:
            self.processing_lock = True
            # Clear previous context to ensure we're starting fresh
            self.current_context.clear()
            
            user_message = "[Image Analysis Request]\n"
            if notes:
                user_message += f"Question: {notes}\n"
            user_message += "[Attached Image]"
            self.current_context.append((user_message, "user"))
            self.image_processed_signal.emit("", image)
            self.processing_started.emit()
            
            # Clean up any previous image processing before starting a new one
            self._cleanup_previous_image_processing()
            
            self.worker_thread = QThread()
            self.worker = ImageWorker(image, notes)
            self.worker.moveToThread(self.worker_thread)
            self.worker_thread.started.connect(self.worker.process)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.response_ready.connect(lambda response: self._handle_image_response(response, image, notes))
            self.worker.error.connect(lambda e: self.error_occurred.emit(f"Error processing image: {e}"))
            self.worker.progress.connect(self.image_progress.emit)
            self.worker.stream_chunk.connect(self._handle_stream)
            self.image_progress.emit(0)
            self.worker_thread.start()
            
            # Set the last request type to image
            self.last_request_type = "image"
        except Exception as e:
            self.error_occurred.emit(f"Error setting up image processing: {str(e)}")
            self.processing_lock = False
        finally:
            QApplication.processEvents()

    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        return self.paused

    def set_paused(self, paused: bool) -> None:
        self.paused = paused

    def process_with_notes(self, notes: str):
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
        if not self.last_copied_text:
            self.error_occurred.emit("No content found to process with notes")
            return
        try:
            self.processing_lock = True
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
            self.last_request_type = "text"
            self.last_copied_text = None
        except Exception as e:
            self.error_occurred.emit(f"Error processing with notes: {str(e)}")
        finally:
            self.processing_lock = False

    def request_notes(self):
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
        if self.processing_lock:
            return False
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                QApplication.processEvents()
                if retry_count > 0:
                    QTimer.singleShot(250, lambda: None)
                    QApplication.processEvents()
                mime_data = self.clipboard.mimeData()
                if mime_data and mime_data.hasImage():
                    image = mime_data.imageData()
                    if image and not image.isNull():
                        self.last_copied_image = image
                        return True
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
        if self.processing_lock:
            self.error_occurred.emit("Please wait, currently processing previous content")
            return
        if not self.last_copied_image:
            self.error_occurred.emit("No image found to process with notes")
            return
        try:
            self.processing_lock = True
            self.process_image(self.last_copied_image, notes)
            self.last_request_type = "image"
            self.last_copied_image = None
        except Exception as e:
            self.error_occurred.emit(f"Error processing image with notes: {str(e)}")
        finally:
            self.processing_lock = False

    def _handle_image_response(self, response: str, image: QImage = None, notes: str = None):
        try:
            # Don't add the user message again since we already added it in process_image
            # Just add the assistant response
            self.current_context.append((response, "assistant"))
            self.content_processed.emit(response)
            if image:
                display_image = QImage(image)
                self.image_processed_signal.emit(response, display_image)
        except Exception as e:
            self.error_occurred.emit(f"Error handling image response: {str(e)}")
        finally:
            self.processing_lock = False

    def _cleanup_previous_image_processing(self):
        try:
            if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(1000)
            self.processing_lock = False
        except Exception as e:
            print(f"Error cleaning up image processing: {str(e)}")
