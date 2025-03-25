# Clipboard AI

**Clipboard AI** is a powerful desktop application that seamlessly integrates with your system clipboard to process content using local Large Language Models (LLMs) through Ollama. This application runs in your system tray, continuously monitoring your clipboard, and can process both text and images either automatically or triggered by customizable hotkeys.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Processing Modes](#processing-modes)
  - [Hotkeys](#hotkeys)
  - [Settings](#settings)
  - [Image Processing](#image-processing)
  - [Text Processing](#text-processing)
  - [Notes Feature](#notes-feature)
- [Technical Details](#technical-details)
  - [Core Components](#core-components)
  - [Multi-threading Design](#multi-threading-design)
  - [Communication Flow](#communication-flow)
  - [Configuration System](#configuration-system)
  - [UI Components](#ui-components)
- [Development](#development)
  - [Environment Setup](#environment-setup)
  - [Code Structure](#code-structure)
  - [Adding New Features](#adding-new-features)
- [Building Executables](#building-executables)
  - [Windows](#windows)
  - [macOS](#macos)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)

## Overview

Clipboard AI is designed to enhance your productivity by automatically processing text and images you copy to your clipboard. Using the power of local LLMs through Ollama, it can analyze, summarize, and transform content without sending your data to external services, ensuring privacy and security.

The application sits unobtrusively in your system tray, working silently in the background. When text or an image is copied to your clipboard, Clipboard AI can either automatically process it (Auto mode) or wait for you to trigger processing with a customizable hotkey (Manual mode).

## Features

- **System Tray Integration**: Unobtrusive presence with easy access to settings and controls
- **Clipboard Monitoring**: Real-time monitoring of text and image content in your clipboard
- **Dual Processing Modes**:
  - **Auto Mode**: Automatically processes new clipboard content
  - **Manual Mode**: Only processes when triggered by a configurable hotkey
- **Multi-modal Processing**:
  - **Text Processing**: Analyzes, summarizes, or transforms text content
  - **Image Processing**: Analyzes and describes images with vision-capable models
- **Ollama Integration**: Seamless connection to local LLMs for on-device processing
- **Customizable Hotkeys**: Configure different hotkeys for text processing, image processing, and notes
- **Floating Response Dialog**: Displays AI responses in a modern, user-friendly interface
- **Conversational Context**: Maintains context for follow-up questions
- **Notes Feature**: Add context or instructions for more precise AI responses
- **Cross-platform Support**: Works on Windows and macOS

## Architecture

Clipboard AI follows a modular architecture with these key components:

1. **Main Application (ClipboardAI)**: Coordinates between all components
2. **Clipboard Monitor**: Monitors system clipboard for changes
3. **Ollama Integration**: Communicates with the Ollama API
4. **UI Components**: System tray, floating dialog, and settings interfaces
5. **Worker Components**: Handles processing in background threads
6. **Configuration System**: Manages user preferences and settings

The application uses PyQt6 for the GUI and multi-threading capabilities, with a signal-based communication pattern for asynchronous operations.

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- One or more of the following models pulled in Ollama:
  - `gemma3:latest` - General purpose text and image model
  - `deepseek-r1:8b` - Alternative text model
  - Any other compatible models that support text and/or image processing

## Installation

### From Source

1. Ensure you have Python 3.8+ installed
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

### Using Pre-built Binaries

1. Download the latest release for your platform from the [Releases](https://github.com/Likithmeruvu/clipboard_ai/releases) page
2. Install Ollama from [ollama.ai](https://ollama.ai)
3. Run the executable file

## Usage

### Preparing Ollama

1. Make sure Ollama is running on your system
2. Pull at least one of the supported models:
   ```bash
   ollama pull gemma3:latest
   # or
   ollama pull deepseek-r1:8b
   ```

### Starting the Application

Run the application using one of these methods:

- **If installed via pip**:
   ```bash
   clipboard-ai
   ```
- **If using pre-built binary**:
  Simply double-click the executable

The application will appear in your system tray with an icon. Right-click the icon to access the menu.

### Processing Modes

The application operates in two modes:

1. **Auto Mode**: Automatically processes any new content detected in the clipboard
2. **Manual Mode** (default): Only processes clipboard content when you press the configured hotkey

You can switch between modes in the settings dialog or via the system tray menu.

### Hotkeys

Clipboard AI uses several configurable hotkeys:

- **Process Text** (default: `Ctrl+Shift+U`): Process the current clipboard content
- **Add Notes** (default: `Ctrl+Shift+.`): Add context or instructions for processing
- **Process Image** (default: `Ctrl+Shift+,`): Process an image in the clipboard

All hotkeys can be customized in the settings dialog.

### Settings

Access the settings dialog by right-clicking the system tray icon and selecting "Settings". Here you can configure:

- **Processing Mode**: Choose between Auto and Manual modes
- **Hotkeys**: Customize the key combinations for different functions
- **LLM Model Selection**: Choose which Ollama model to use for text and image processing
- **Ollama Host**: Configure the URL where Ollama is running (default: http://localhost:11434)
- **Notification Duration**: Set how long notifications are displayed

### Image Processing

When an image is copied to your clipboard:

1. In **Auto Mode**, a dialog will automatically appear asking for optional notes about how to process the image
2. In **Manual Mode**, press the image processing hotkey to trigger the dialog
3. Add optional notes to guide the AI's analysis
4. The AI will process the image and display results in the floating dialog

### Text Processing

When text is copied to your clipboard:

1. In **Auto Mode**, the text is automatically sent to the AI for processing
2. In **Manual Mode**, press the text processing hotkey to send the text to the AI
3. Results appear in the floating dialog where you can also ask follow-up questions

### Notes Feature

The notes feature allows you to add context or specific instructions for processing:

1. Copy text or an image to your clipboard
2. Press the notes hotkey
3. Enter your notes or instructions in the dialog
4. Click "Process" to send both the clipboard content and your notes to the AI

## Technical Details

### Core Components

#### ClipboardAI (main.py)
The central orchestrator that initializes all components and manages communication between them.

#### ClipboardMonitor (clipboard_monitor.py)
Responsible for monitoring the system clipboard for changes and detecting both text and images.

#### OllamaAPI (ollama_integration.py)
Handles all communication with the Ollama API, including model selection, streaming responses, and processing both text and images.

#### TextWorker and ImageWorker (text_worker.py, image_worker.py)
Background workers that process text and images asynchronously to keep the UI responsive.

#### HotkeyManager (hotkey_manager.py)
Manages global hotkey registration and triggering callbacks when hotkeys are pressed.

#### Config (config.py)
Handles loading, saving, and accessing user configuration settings.

### Multi-threading Design

Clipboard AI uses Qt's threading capabilities to ensure UI responsiveness:

1. **Main Thread**: Handles UI operations and user interaction
2. **Text Worker Thread**: Processes text in the background
3. **Image Worker Thread**: Processes images in the background

Communication between threads is managed through Qt's signals and slots mechanism.

### Communication Flow

1. User copies content → Clipboard change detected → ClipboardMonitor processes change
2. ClipboardMonitor creates appropriate worker (TextWorker/ImageWorker)
3. Worker communicates with Ollama through OllamaAPI
4. OllamaAPI streams responses back → Worker emits signals → UI updates with results

### Configuration System

The configuration system (config.py) handles user preferences:

- Settings are stored in JSON format at `<user_config_dir>/clipboard_ai/config.json`
- Default settings are provided for first-time users
- Settings include processing mode, hotkeys, model selection, and UI preferences

### UI Components

#### SystemTray (ui/tray.py)
Provides the system tray icon and menu for basic controls and access to settings.

#### FloatingDialog (ui/floating_dialog.py)
Displays AI responses in a modern, floating window with support for markdown formatting, code highlighting, and follow-up questions.

#### SettingsDialog (ui/settings_dialog.py)
Allows users to configure all aspects of the application.

#### ImageDialog (ui/image_dialog.py)
Shows the image being processed and allows adding notes for context.

#### NotesDialog (ui/notes_dialog.py)
Allows adding notes or instructions for processing clipboard content.

## Development

### Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Code Structure

```
clipboard_ai/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point
├── main.py               # Main application class
├── clipboard_monitor.py  # Clipboard monitoring logic
├── ollama_integration.py # Ollama API integration
├── config.py             # Configuration management
├── hotkey_manager.py     # Global hotkey handling
├── text_worker.py        # Background text processing
├── image_worker.py       # Background image processing
├── ui/                   # User interface components
│   ├── __init__.py       # UI package initialization
│   ├── tray.py           # System tray implementation
│   ├── floating_dialog.py # Response dialog
│   ├── settings_dialog.py # Settings interface
│   ├── image_dialog.py   # Image processing dialog
│   └── notes_dialog.py   # Notes input dialog
└── resources/            # Application resources
```

### Adding New Features

When adding new features:

1. Determine which component should handle the feature
2. Implement the feature in the appropriate module
3. Add any necessary UI elements
4. Update communication flow using Qt's signals and slots
5. Add configuration options if needed
6. Test thoroughly on all supported platforms

## Building Executables

### Windows

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=clipboard_ai/resources/icon.ico --name=clipboard-ai clipboard_ai/main.py
```

For custom packaging with Inno Setup, use the provided `setup.iss` file:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

### macOS

To create a macOS application bundle:

```bash
pip install py2app
python setup.py py2app
```

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama is running (`ollama serve`)
- Check that models are properly pulled (`ollama list`)
- Verify the Ollama host setting (default: http://localhost:11434)

### Hotkey Not Working

- Check for conflicts with other applications
- Ensure the hotkey is properly registered in settings
- Try a different hotkey combination

### Processing Errors

- Check the model is available in Ollama
- Ensure your Python environment has all required dependencies
- For image processing issues, ensure you have a vision-capable model

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue with suggestions, bug reports, or feature requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
