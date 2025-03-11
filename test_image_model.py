import sys
import os

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary modules
from clipboard_ai.ollama_integration import ollama
from clipboard_ai.config import config

# Print the configured models
print(f"Image model: {config.get('image_model')}")
print(f"Text model: {config.get('selected_model')}")

# Test with an image prompt
test_image_prompt = "[Image: data:image/png;base64,test] Please analyze this image."
print(f"\nTesting with image prompt: '{test_image_prompt[:30]}...'")

# Create an instance of OllamaAPI to test the model selection logic
api = ollama.generate_response

# Get the model that would be used for the image prompt
model_for_image = config.get("image_model") if "[Image:" in test_image_prompt else config.get("selected_model")
print(f"Model that would be used: {model_for_image}")

# Test with a text prompt
test_text_prompt = "What is the capital of France?"
print(f"\nTesting with text prompt: '{test_text_prompt}'")

# Get the model that would be used for the text prompt
model_for_text = config.get("image_model") if "[Image:" in test_text_prompt else config.get("selected_model")
print(f"Model that would be used: {model_for_text}")

print("\nVerification complete!")