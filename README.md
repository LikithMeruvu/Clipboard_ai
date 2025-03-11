# Clipboard AI

A desktop application that monitors your system clipboard and processes content using local LLMs through Ollama. The application runs in the system tray and can process text content either automatically or via a hotkey trigger.

## Features

- System tray integration with easy access to settings and controls
- Automatic or manual (hotkey-triggered) processing of clipboard content
- Integration with Ollama for local LLM processing
- Configurable settings including processing mode, hotkey, and model selection
- Cross-platform support (Windows and macOS)

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- One of the following Ollama models:
  - gemma2:9b-instruct-q3_K_M
  - deepseek-r1:8b

## Installation

1. Make sure you have Python 3.8+ installed
2. Install Ollama from [ollama.ai](https://ollama.ai)
3. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/clipboard_ai.git
   cd clipboard_ai
   ```

4. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

1. Start Ollama and pull one of the supported models:
   ```bash
   ollama pull gemma2:9b-instruct-q3_K_M
   # or
   ollama pull deepseek-r1:8b
   ```

2. Run the application:
   ```bash
   clipboard-ai
   ```

3. The application will appear in your system tray. Right-click the icon to:
   - Toggle between Auto and Manual processing modes
   - Pause/Resume clipboard monitoring
   - Access settings
   - Quit the application

### Settings

Access the settings dialog to configure:
- Processing Mode (Auto/Manual)
- Hotkey combination for manual processing
- LLM model selection

### Processing Modes

1. **Auto Mode**: Automatically processes new clipboard content
2. **Manual Mode**: Only processes clipboard content when the configured hotkey is pressed

## Development

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

## Building Executables

### Windows

To create a Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name=clipboard-ai clipboard_ai/main.py
```

### macOS

To create a macOS application:

```bash
pip install py2app
python setup.py py2app
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
