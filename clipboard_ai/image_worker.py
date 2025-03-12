from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
import base64
from PyQt6.QtCore import QByteArray, QBuffer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .ollama_integration import ollama
from .config import config
import tempfile
import os
import uuid

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
        temp_file_path = None
        try:
            # Report progress
            self.progress.emit(10)
            
            # Create a unique temporary file name with a UUID
            unique_id = str(uuid.uuid4())
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"clipboard_ai_image_{unique_id}.jpg")
            
            # If image is very large, scale it down to reduce processing time
            if self.image.width() > 1200 or self.image.height() > 1200:
                scaled_image = self.image.scaled(
                    1200, 1200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # Save the scaled image to the temporary file
                scaled_image.save(temp_file_path, "JPG", 85)  # Use JPG with 85% quality for better compression
            else:
                # Save the original image to the temporary file
                self.image.save(temp_file_path, "JPG", 90)
            
            # Report progress
            self.progress.emit(30)
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
            # Report progress
            self.progress.emit(40)
            
            # Create prompt based on whether notes were provided
            if self.notes:
                prompt = f"I'm going to show you an image. Please analyze it according to these instructions: {self.notes}\n\n"
            else:
                prompt = f"I'm going to show you an image. Please analyze it and describe what you see in detail.\n\n"
            
            # Log the prompt format
            print(f"Using prompt: {prompt[:100]}...")
            print(f"Image saved to temporary file: {temp_file_path}")
            
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
                
                # Read the image file and encode it to base64
                with open(temp_file_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Use the chat API with the image in the messages array
                response = ollama.chat(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt, "images": [encoded_image]}
                    ],
                    stream=True,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                )
                
                # Process the streaming response
                full_response = ""
                for chunk in response:
                    if "message" in chunk and "content" in chunk["message"]:
                        text = chunk["message"]["content"]
                        full_response += text
                        on_stream(text)
                
                # Log successful response
                print("Received complete response from Ollama API")
                
                # Report progress
                self.progress.emit(90)
                
                # Return the full response
                response = full_response.strip()
                
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
            # Clean up the temporary file if it exists
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"Temporary image file removed: {temp_file_path}")
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")
            
            # Signal that processing is complete
            self.finished.emit()
