# Clipboard AI 🚀

A powerful desktop AI assistant that lives in your system tray. Copy text or images, and let AI analyze them instantly - all running locally on your machine using Ollama.

![GitHub License](https://img.shields.io/github/license/LikithMeruvu/Clipboard_ai)

## ✨ What It Does

- 📋 Monitors your clipboard for text and images
- 🤖 Processes content using local AI (no data sent to cloud)
- 💬 Provides AI analysis and insights instantly
- 🖼️ Analyzes both text and images
- 🔥 Works with hotkeys or automatically

## 🚀 Quick Start

1. **Install Prerequisites**
   ```bash
   # 1. Install Python 3.8+
   # 2. Install Ollama from https://ollama.ai
   # 3. Pull required models:
   ollama pull gemma3:latest  # for text
   ollama pull llava:latest   # for images
   ```

2. **Install Clipboard AI**
   ```bash
   # Clone and install
   git clone https://github.com/LikithMeruvu/clipboard_ai.git
   cd clipboard_ai
   pip install -e .

   # Or download the Windows executable
   # clipboard-ai.exe from releases
   ```

3. **Run It**
   ```bash
   clipboard-ai
   ```

## 🎮 How to Use

### Text Analysis
1. Copy any text
2. Press `Ctrl+Shift+U` (or wait if in auto mode)
3. Get instant AI analysis!

### Image Analysis
1. Copy an image
2. Press `Ctrl+Shift+,`
3. Add notes if needed
4. Get AI insights about your image!

### Quick Tips
- Right-click tray icon for settings
- Add notes to any analysis with `Ctrl+Shift+.`
- Ask follow-up questions in the chat window
- Switch between auto/manual modes in settings

## ⚙️ Settings

Access settings through the tray icon:
- **Processing Mode**: Auto or Manual (hotkey)
- **Models**: Choose your preferred AI models
- **Hotkeys**: Customize keyboard shortcuts
  - Text Analysis: `Ctrl+Shift+U`
  - Image Analysis: `Ctrl+Shift+,`
  - Add Notes: `Ctrl+Shift+.`

## 🛠️ Development

### Setup Dev Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"
```

### Build Executables

**Windows**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=clipboard_ai/resources/icon.ico --name=clipboard-ai clipboard_ai/main.py
```

**macOS**
```bash
pip install py2app
python setup.py py2app
```

## 🤝 Contributing

Contributions welcome! Some areas you can help with:
- Additional model support
- UI improvements
- New content types (PDFs, code)
- Linux support
- Performance optimizations

## 📝 License

MIT License - feel free to use and modify!