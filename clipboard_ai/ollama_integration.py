import requests
import json
from typing import Dict, Any, List, Optional, Callable, Generator, Union
from .config import config
import base64

class OllamaAPI:
    def __init__(self):
        self.base_url = config.get("ollama_host")
        self.session = requests.Session()

    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> List[Dict[str, str]]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except requests.RequestException as e:
            print(f"Error listing models: {e}")
            return []

    def generate_stream(self, prompt: str, image_data: Optional[bytes] = None) -> Generator[str, None, None]:
        """Generate a streaming response from Ollama."""
        try:
            # Use different model based on whether we have image data
            model = config.get("image_model") if image_data else config.get("selected_model")
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
            
            # Add image data if provided
            if image_data:
                data["images"] = [base64.b64encode(image_data).decode()]

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=data,
                stream=True
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"Error: {response.status_code} - {response.text}"

        except requests.RequestException as e:
            yield f"Error communicating with Ollama: {str(e)}"

    def generate(self, model: str, prompt: str, stream: bool = True, options: dict = None) -> Union[dict, Generator]:
        """Generate a response from Ollama with support for multimodal inputs."""
        try:
            # Prepare the API endpoint
            url = f"{self.base_url}/api/generate"
            
            # Prepare the payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            # Add options if provided
            if options:
                payload["options"] = options
    
            # Make the API call
            response = requests.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._process_stream(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Failed to generate response: {str(e)}")

    def generate_response(self, prompt: str, model: Optional[str] = None, on_stream: Optional[Callable[[str], None]] = None, timeout: int = 60) -> str:
        """Generate a response using the specified model with streaming support."""
        # Determine if this is an image request
        is_image_request = "[Image:" in prompt
        request_type = "image" if is_image_request else "text"
        
        # Use image_model for image requests if no specific model is provided
        if model is None:
            model = config.get("image_model") if is_image_request else config.get("selected_model")
        
        print(f"Starting {request_type} request to Ollama API with model: {model}")
        print(f"Prompt length: {len(prompt)} characters")
        
        try:
            # Add timeout to prevent hanging indefinitely
            print(f"Sending request to {self.base_url}/api/generate")
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                stream=True,
                timeout=timeout
            )
            
            print(f"Received initial response with status code: {response.status_code}")
            
            if response.status_code == 200:
                full_response = ""
                chunk_count = 0
                print("Starting to process response stream...")
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                text = chunk["response"]
                                full_response += text
                                chunk_count += 1
                                if chunk_count % 10 == 0:
                                    print(f"Processed {chunk_count} chunks so far")
                                if on_stream:
                                    on_stream(text)
                        except json.JSONDecodeError as json_err:
                            print(f"JSON decode error: {str(json_err)} on line: {line[:100]}...")
                            continue
                        except Exception as chunk_err:
                            print(f"Error processing chunk: {str(chunk_err)}")
                            continue
                
                print(f"Completed processing {chunk_count} chunks from Ollama")
                return full_response.strip()
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                print(f"API error: {error_msg}")
                if on_stream:
                    on_stream(error_msg)
                return error_msg
                
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout error communicating with Ollama: {str(e)}"
            print(error_msg)
            if on_stream:
                on_stream(error_msg)
            return error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error with Ollama: {str(e)}"
            print(error_msg)
            if on_stream:
                on_stream(error_msg)
            return error_msg
        except requests.RequestException as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            print(error_msg)
            if on_stream:
                on_stream(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error in generate_response: {str(e)}"
            print(error_msg)
            if on_stream:
                on_stream(error_msg)
            return error_msg

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.RequestException:
            return {}

    def _process_stream(self, response) -> Generator[str, None, None]:
        """Process a streaming response from Ollama."""
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"Error processing stream: {str(e)}"

# Global Ollama API instance
ollama = OllamaAPI()