# Clipboard AI

A desktop application that monitors your system clipboard and processes content using local language models through Ollama. The application runs in the system tray and can intelligently analyze both text and images with AI, triggered either automatically or via customizable hotkeys.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Setup and Configuration](#setup-and-configuration)
- [Usage](#usage)
  - [Text Processing](#text-processing)
  - [Image Processing](#image-processing)
  - [Adding Notes](#adding-notes)
  - [Follow-up Questions](#follow-up-questions)
- [Settings and Customization](#settings-and-customization)
- [Technical Implementation](#technical-implementation)
  - [Main Components](#main-components)
  - [Core Classes](#core-classes)
  - [UI Components](#ui-components)
  - [Ollama Integration](#ollama-integration)
- [Building from Source](#building-from-source)
- [Development Environment](#development-environment)
- [License](#license)
- [Contributing](#contributing)

## Overview

Clipboard AI enhances your workflow by seamlessly integrating AI processing capabilities into your clipboard operations. The application uses Ollama to run local large language models (LLMs) that can process both text and images copied to your clipboard, providing instant AI analysis and assistance without sending your data to remote servers.

## Key Features

- **System Tray Integration**: Always accessible yet unobtrusive, the application runs in your system tray
- **Multi-Modal AI Processing**: Supports both text and image analysis through local LLMs
- **Flexible Processing Modes**:
  - **Auto Mode**: Automatically processes new clipboard content
  - **Manual Mode**: Processes clipboard content only when triggered by hotkeys
- **Customizable Hotkeys**: Configure separate hotkeys for text processing, image analysis, and notes
- **Interactive User Interface**: Floating dialog for viewing AI responses with the ability to ask follow-up questions
- **Rich Image Analysis**: Dedicated image processing workflow with notes capability
- **Contextual Conversations**: Support for maintaining context in follow-up questions
- **Local Processing**: All AI processing happens on your machine using Ollama models
- **Cross-Platform**: Works on Windows and macOS

## Architecture

Clipboard AI uses a modular, event-driven architecture based on PyQt6 with these major components:

```
clipboard_ai/
├── __init__.py            # Package initialization
├── __main__.py            # Entry point
├── clipboard_monitor.py   # Core clipboard monitoring
├── config.py              # Configuration management
├── hotkey_manager.py      # Keyboard shortcut handling
├── image_worker.py        # Dedicated image processing
├── main.py                # Main application logic
├── ollama_integration.py  # API integration with Ollama
├── text_worker.py         # Text processing worker
├── resources/             # Application resources
└── ui/                    # User interface components
    ├── floating_dialog.py # Main response dialog
    ├── image_dialog.py    # Image processing dialog
    ├── notes_dialog.py    # Notes input dialog
    ├── settings_dialog.py # Settings configuration
    └── tray.py            # System tray integration
```

## Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- One of the following Ollama models for text processing:
  - gemma3:latest (recommended)
  - gemma2:9b-instruct-q3_K_M
  - deepseek-r1:8b
- One of the following Ollama models for image processing:
  - llava:latest (recommended)
  - bakllava:latest
  - gemma3:latest (supports images with newer versions)

### Installation Steps

1. Make sure you have Python 3.8+ installed
2. Install Ollama from [ollama.ai](https://ollama.ai)
3. Clone this repository:
   ```bash
   git clone https://github.com/Likithmeruvu/clipboard_ai.git
   cd clipboard_ai
   ```

4. Install the package:
   ```bash
   pip install -e .
   ```

### Alternative: Direct Installation

You can use the pre-built executable for Windows:
- Download `clipboard-ai.exe` from the repository
- Run the executable directly (no installation needed)

## Setup and Configuration

1. Start Ollama and pull at least one supported model for text and one for image processing:
   ```bash
   # For text processing
   ollama pull gemma3:latest
   
   # For image processing
   ollama pull llava:latest
   ```

2. On first launch, ensure Ollama is running. The application will check for required models and notify you if any are missing.

3. By default, the application starts in Manual mode, using hotkeys to trigger processing. You can change this in settings.

## Usage

Run the application with:
```bash
clipboard-ai
```

The application will appear in your system tray. Right-click the tray icon to access the menu.

### Text Processing

1. **Auto Mode**: Copy any text, and it will be automatically processed by the AI
2. **Manual Mode**: 
   - Copy text to your clipboard
   - Press the configured hotkey (default: `Ctrl+Shift+U`)
   - A floating dialog will appear with the AI's response

### Image Processing

1. Copy an image to your clipboard
2. Use the image hotkey (default: `Ctrl+Shift+,`)
3. An image dialog will appear allowing you to add notes or specific questions about the image
4. After submitting, the AI will analyze the image and display the results in the floating dialog

### Adding Notes

For text content, you can add your own notes or questions:
1. Copy text to your clipboard
2. Press the notes hotkey (default: `Ctrl+Shift+.`)
3. Enter your notes or questions in the dialog
4. The AI will process both the text and your notes together

### Follow-up Questions

After receiving a response in the floating dialog:
1. Type your follow-up question in the input field at the bottom
2. Press Enter or click the Send button
3. The AI will respond in context of the previous conversation

## Settings and Customization

Access settings by right-clicking the tray icon and selecting "Settings". You can configure:

- **Processing Mode**: Choose between Auto (automatic processing) and Manual (hotkey-triggered)
- **Hotkeys**:
  - Text processing hotkey (default: `Ctrl+Shift+U`)
  - Image processing hotkey (default: `Ctrl+Shift+,`)
  - Notes hotkey (default: `Ctrl+Shift+.`)
- **Models**:
  - Select different text and image processing models from your installed Ollama models
  - Refresh the model list if you've installed new models

## Technical Implementation

### Main Components

#### ClipboardAI Class
The central orchestration class that initializes and connects all components, handles signals between components, and manages the application lifecycle.

#### ClipboardMonitor
Monitors the system clipboard for changes, detects content type (text or image), and delegates processing to appropriate workers.

#### OllamaAPI
Provides a comprehensive interface to the Ollama API, handling both text and image processing through the local Ollama service.

#### Config
Manages persistent application settings using JSON storage in the user's config directory.

### Core Classes

#### TextWorker
- Offloads text processing to a separate thread
- Handles prompt construction and streaming responses
- Maintains conversation context for follow-up questions

#### ImageWorker
- Dedicated worker for image processing
- Handles image conversion, optimization, and base64 encoding
- Supports streaming responses for real-time feedback

#### HotkeyManager
- Manages global hotkey registration and event handling
- Supports configurable key combinations for different functions

### UI Components

#### SystemTray
- Provides access to the application through system tray icon
- Includes menu for accessing settings, pausing/resuming, and quitting

#### FloatingDialog
- Displays AI responses in a chat-like interface
- Supports conversation history and follow-up questions
- Features a thinking widget for processing status

#### SettingsDialog
- Configures application settings including processing mode, hotkeys, and models
- Validates Ollama connection and available models
- Persists settings through the Config class

#### ImageDialog & NotesDialog
- Specialized dialogs for image annotation and adding notes to text
- Provide contextual input for enhanced AI processing

### Ollama Integration

The application communicates with Ollama through its REST API, supporting:
- Text generation with streaming responses
- Image analysis using multimodal models
- Model information retrieval and validation
- Response streaming for improved user experience

## Building from Source

### Windows

To create a Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=clipboard_ai/resources/icon.ico --name=clipboard-ai clipboard_ai/main.py
```

### macOS

To create a macOS application:

```bash
pip install py2app
python setup.py py2app
```

## Development Environment

To set up the development environment:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Areas for potential enhancement:
- Additional model support
- Enhanced image processing capabilities
- Improved UI themes and customization
- Support for more content types (PDFs, code files)
- Memory management optimizations
- Extended platform support (Linux)