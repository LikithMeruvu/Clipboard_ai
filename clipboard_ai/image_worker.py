from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
import base64
from PyQt6.QtCore import QByteArray, QBuffer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .ollama_integration import ollama
from .config import config

class ImageWorker(QObject):
    finished = pyqtSignal()  # Signal emitted when processing is complete
    response_ready = pyqtSignal(str)  # Signal emitted when response is ready
    error = pyqtSignal(str)  # Signal emitted when an error occurs
    progress = pyqtSignal(int)  # Signal emitted to update progress
    stream_chunk = pyqtSignal(str)  # Signal emitted for each stream chunk
    
    def __init__(self, image: QImage, notes: str = None):
        super().__init__()
        self.image = image
        self.notes = notes
        self.response_text = ""
        
    def process(self):
        """Process the image and generate a response."""
        try:
            # Report progress
            self.progress.emit(10)
            
            # Convert QImage to bytes using QByteArray - optimize by reducing image size if large
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            
            # If image is very large, scale it down to reduce processing time
            if self.image.width() > 1200 or self.image.height() > 1200:
                scaled_image = self.image.scaled(
                    1200, 1200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled_image.save(buffer, "JPG", 85)  # Use JPG with 85% quality for better compression
            else:
                self.image.save(buffer, "JPG", 90)
                
            image_data = byte_array.data()
            
            # Report progress
            self.progress.emit(30)
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
            # Encode image data to base64
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            
            # Report progress
            self.progress.emit(40)
            
            # Create prompt based on whether notes were provided
            # Format the prompt specifically for the Janus model
            if self.notes:
                prompt = (
                    f"I'm going to show you an image. Please analyze it according to these instructions: {self.notes}\n\n"
                    f"[Image: data:image/jpeg;base64,{encoded_image}]"
                )
            else:
                prompt = (
                    f"I'm going to show you an image. Please analyze it and describe what you see in detail.\n\n"
                    f"[Image: data:image/jpeg;base64,{encoded_image}]"
                )
                
            # Log the prompt format (without the actual base64 data)
            print(f"Using prompt format: {prompt[:100]}... [base64 data] ...")
            
            # Report progress
            self.progress.emit(50)
            
            # Process events before model call
            QApplication.processEvents()
            
            try:
                # Log that we're about to call the API
                print("Calling Ollama API for image processing...")
                
                # Always use the image model from config
                model = config.get("image_model")
                print(f"Using model: {model} for image processing")
                
                # Stream the response to improve user experience
                self.response_text = ""
                
                # Define a callback for streaming
                def on_stream(chunk):
                    self.response_text += chunk
                    self.stream_chunk.emit(chunk)
                    # Process events to keep UI responsive
                    QApplication.processEvents()
                
                # Get model response with streaming for vision model
                response = ollama.generate_response(
                    prompt, 
                    model=model,
                    on_stream=on_stream,
                    timeout=120  # Increase timeout for image processing
                )
                
                # Log successful response
                print("Received complete response from Ollama API")
                
                # Report progress
                self.progress.emit(90)
            except Exception as e:
                # Log the specific error
                error_msg = f"Error during Ollama API call: {str(e)}"
                print(error_msg)
                self.error.emit(error_msg)
                # Still emit progress to avoid UI getting stuck
                self.progress.emit(100)
                # Re-raise to be caught by outer exception handler
                raise
            
            # Process events after getting response
            QApplication.processEvents()
            
            # Emit the complete response
            self.response_ready.emit(response)
            
            # Report completion
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Signal that processing is complete
            self.finished.emit()
