# clipboard_ai/text_worker.py
from PyQt6.QtCore import QObject, pyqtSignal
from clipboard_ai.ollama_integration import ollama
from clipboard_ai.config import config

class TextWorker(QObject):
    finished = pyqtSignal()
    result_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    stream_chunk = pyqtSignal(str)

    def __init__(self, prompt: str, is_follow_up: bool = False, context: list = None):
        super().__init__()
        self.prompt = prompt
        self.is_follow_up = is_follow_up
        self.context = context if context is not None else []

    def process(self):
        try:
            # If it is a follow-up and context exists, build a composite prompt
            if self.is_follow_up and self.context:
                context_str = "\n".join([
                    f"{'User' if role == 'user' else 'Assistant'}: {content}"
                    for content, role in self.context
                ])
                self.prompt = f"{context_str}\n\nUser: {self.prompt}\n\nAssistant: Let me help you with that follow-up question."
            full_response = ""
            # Stream the response from Ollama in a non-blocking way
            for chunk in ollama.generate_stream(self.prompt):
                full_response += chunk
                self.stream_chunk.emit(chunk)
            self.result_ready.emit(full_response.strip())
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
