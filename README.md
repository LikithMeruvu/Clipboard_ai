**Planning search queries**

I’m brainstorming a list of search queries based on the user's topics of interest. They seem to want a comprehensive list of sources and citations. I’ll make sure to include both documentation types (like GitHub, PyQt6, PyInstaller) and related guides. The goal is to gather at least 15 high-quality sources to cover all these topics thoroughly — including READMEs, cross-platform packaging, system tray applications, and licenses. It’s clear I want to focus on detailed docs and examples.


**Finalizing search queries**

I’ll run a batch of search queries based on various documentation and guides, pulling from multiple sources ranging from GitHub best practices to library documentation on PyQt, PyInstaller, and more. There’s a slight worry some of the results might not be directly relevant, but I have plenty to work with. The goal is to gather at least 15 high-quality sources to properly craft the README, with citations referencing each source. I'll need to integrate them coherently, but the core approach is to cover all bases.

**Crafting README with citations**

I’m thinking through how to integrate citations into the README. Since it’s inside a code block, I can’t directly embed citations there, as it could break the formatting. I’ll have to place them outside the code section, perhaps in a "References" or "Further Reading" section. Citations should follow each sentence where external sources are referenced, but I’ll keep the content within the README code block original and example-focused. A footnote-comment approach might even work for non-visible citations. I’ll need to make sure the guidelines are all followed!


Thought for 37 seconds


Below is a production‑grade **README.md** you can drop straight into **`LikithMeruvu/Clipboard_ai`**.
It follows current GitHub best‑practice structure (badges, clear value prop, install matrix, architecture diagram, security disclaimers, contribution guide, etc.) and is long enough to double as product documentation. Replace image placeholders (`.github/assets/...`) with real screenshots or GIFs when you have them.

````markdown
<!-- Banner -->
<p align="center">
  <img src="https://raw.githubusercontent.com/LikithMeruvu/Clipboard_ai/main/.github/assets/banner.png" alt="Clipboard AI banner" width="90%">
</p>

<h1 align="center">Clipboard AI</h1>
<p align="center">
  <b>Turn copy‑paste into super‑powers.</b><br>
  Analyse, summarise and transform text <em>and</em> images in your clipboard using local LLMs – in one hot‑key – without sending your data anywhere.
</p>

<p align="center">
  <a href="https://github.com/LikithMeruvu/Clipboard_ai/actions"><img alt="CI status" src="https://img.shields.io/github/actions/workflow/status/LikithMeruvu/Clipboard_ai/ci.yml?label=build&logo=github&style=for-the-badge"></a>
  <a href="https://github.com/LikithMeruvu/Clipboard_ai/releases"><img alt="Downloads" src="https://img.shields.io/github/downloads/LikithMeruvu/Clipboard_ai/total?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/LikithMeruvu/Clipboard_ai/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/LikithMeruvu/Clipboard_ai?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/LikithMeruvu/Clipboard_ai/blob/main/LICENSE"><img alt="Licence" src="https://img.shields.io/github/license/LikithMeruvu/Clipboard_ai?style=for-the-badge"></a>
</p>

> **TL;DR** – Clipboard AI sits in your system tray, watches your clipboard and—when you hit a hot‑key or let it auto‑trigger—pipes the content through local LLMs served by **Ollama**. The result (summary, explanation, caption, code refactor, whatever) streams back in a sleek floating chat window that remembers context.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Demo](#demo)
3. [How It Works](#how-it-works)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Configuration](#configuration)
7. [Supported Models](#supported-models)
8. [Security & Privacy](#security--privacy)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap](#roadmap)
11. [Contributing](#contributing)
12. [License](#license)
13. [Credits](#credits)

---

## Key Features
- **System‑tray daemon** – lives quietly in Windows & macOS menu bars; built with PyQt6 and `QSystemTrayIcon`.
- **Global hot‑keys** – defaults:  
  `Ctrl + Shift + U` (text) • `Ctrl + Shift + O` (image) • `Ctrl + Shift + .` (notes) – all user‑configurable.
- **Auto vs Manual** – let Clipboard AI auto‑process every copy or only when you press a key.
- **Multimodal** – processes plain text, rich text and images (captured or files) with vision‑capable models.
- **Contextual chat** – follow‑up questions stay in‑memory so you can iterate without re‑copying.
- **100 % Local** – powered by [Ollama](https://ollama.ai) models: no cloud calls, so your data never leaves the machine.
- **Cross‑platform packaging** – single‑file executables via PyInstaller (Windows) and py2app (macOS) plus Inno Setup installer.
- **Extensible** – modular worker threads; just swap models or add new prompts to extend functionality.
- **Private config** – JSON settings stored in platform‑correct user config dir (thanks `appdirs`).

---

## Demo
| Auto‑mode instant summary | Image caption with notes | Follow‑up Q&A |
|---|---|---|
| ![auto‑text](.github/assets/demo_autotext.gif) | ![image‑caption](.github/assets/demo_image.gif) | ![chat](.github/assets/demo_followup.gif) |

---

## How It Works
```mermaid
flowchart LR
  subgraph UI
    Tray(System Tray)
    Dialog(Floating Chat UI)
    Settings(Settings Dialog)
  end
  Clipboard(Clipboard Monitor) -->|signals| Workers
  Workers -->|threads| Ollama(Ollama API Service)
  Ollama -->|stream| Dialog
  Tray --> Dialog
  Settings --> Tray
````

1. **ClipboardMonitor** watches clipboard via Qt’s `QClipboard` and emits signals when it detects new text/image.
2. **Worker threads** (TextWorker & ImageWorker) call Ollama’s OpenAI‑compatible REST endpoints, streaming tokens back.
3. **FloatingDialog** displays a thinking indicator then streams the response; users can ask follow‑up questions that keep context.
4. **SystemTray** menu lets you pause, switch Auto/Manual mode, open Settings, or quit.

---

## Installation

### 1. Prerequisites

| Dependency | Minimum  | Notes                                                 |
| ---------- | -------- | ----------------------------------------------------- |
| **Python** |  3.8     | Only needed if installing from source                 |
| **Ollama** | latest   | `brew install ollama` / Windows MSI / Docker          |
| **GPU**    | Optional | CPU works; GPU + 8 GB VRAM recommended for >7B models |

### 2. Grab a Release (recommended)

```text
🪟  Windows 10+  →  ClipboardAI‑Setup‑x.y.z.exe
🍎  macOS 12+    →  Clipboard AI‑x.y.z.dmg
```

Download from the **[Releases](https://github.com/LikithMeruvu/Clipboard_ai/releases)** page, install, run. The tray icon appears on first launch.

### 3. Build from Source

```bash
git clone https://github.com/LikithMeruvu/Clipboard_ai.git
cd Clipboard_ai
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -e .
ollama pull gemma3:latest        # or deepseek-r1:8b, llama3, etc.
clipboard-ai                      # launch
```

---

## Usage

| Action                         | Default Shortcut   | What Happens                                          |
| ------------------------------ | ------------------ | ----------------------------------------------------- |
| **Process latest copy**        | `Ctrl + Shift + U` | Opens dialog; sends clipboard text to AI              |
| **Add notes to last copy**     | `Ctrl + Shift + .` | Opens modal for extra instructions                    |
| **Analyse image in clipboard** | `Ctrl + Shift + O` | Shows preview → enter question → get caption/analysis |
| **Toggle Auto/Manual**         | Tray → *Auto‑mode* | Auto processes every new copy                         |
| **Pause / Resume monitoring**  | Tray → *Pause*     | Suspends clipboard hooks                              |

Hot‑keys are editable in **Tray → Settings**.

---

## Configuration

A JSON file is created on first run at:

```text
Windows : %APPDATA%\clipboard_ai\config.json
macOS   : ~/Library/Application Support/clipboard_ai/config.json
Linux   : ~/.config/clipboard_ai/config.json
```

Sample:

```jsonc
{
  "processing_mode": "manual",
  "hotkey": "ctrl+shift+u",
  "notes_hotkey": "ctrl+shift+.",
  "image_hotkey": "ctrl+shift+o",
  "selected_model": "gemma3:latest",
  "image_model": "gemma3:latest",
  "ollama_host": "http://localhost:11434",
  "notification_duration": 5000
}
```

---

## Supported Models

| Purpose | Default         | Alternatives                                         |
| ------- | --------------- | ---------------------------------------------------- |
| Text    | `gemma3:latest` | `deepseek-r1:8b`, `llama3`, any GPTQ/gguf text model |
| Vision  | `gemma3:latest` | `llava`, `bakllava`, `clip‑cap`, etc.                |

Pull with:

```bash
ollama pull gemma3:latest
ollama pull deepseek-r1:8b
```

See **Settings → Model Selection** to swap.

---

## Security & Privacy

Clipboard AI never transmits clipboard data over the internet. All inference happens via Ollama on `localhost`.
No analytics, no telemetry, no 3rd‑party servers.

---

## Troubleshooting

| Symptom                        | Fix                                                                       |
| ------------------------------ | ------------------------------------------------------------------------- |
| **“Cannot connect to Ollama”** | Run `ollama serve` first; ensure `config.json` points to the correct port |
| **Hot‑key not working**        | Check for collisions with other apps; edit shortcut in Settings           |
| **Large image stalls**         | Images >4K are down‑scaled automatically; ensure you have enough RAM/VRAM |
| **PyInstaller build fails**    | Use Python 3.10+, upgrade PyInstaller, add `--hidden-import=PyQt6.sip`    |

---

## Roadmap

* [ ] Linux (Wayland/X11) build & AppImage
* [ ] Clipboard history sidebar
* [ ] Custom prompt templates
* [ ] Plugin SDK for speciality tasks (OCR, code lint, translation)
  See the [open issues](https://github.com/LikithMeruvu/Clipboard_ai/issues) for full backlog.

---

## Contributing

Pull requests are welcome! Please:

1. Open an issue to discuss major changes.
2. Fork → `git checkout -b feat/your-feature`.
3. `pre-commit run --all-files` to pass formatting & lint.
4. Add/adjust unit tests.
5. Submit PR – the CI will run on GitHub Actions.

By contributing you agree to abide by the **Contributor Covenant Code of Conduct** (see `CODE_OF_CONDUCT.md`).

---

## License

Clipboard AI is released under the **MIT License** – see [`LICENSE`](LICENSE) for details.

---

## Credits

| Role        | Name / Project                                   |
| ----------- | ------------------------------------------------ |
| Inspiration | Tom Preston‑Werner’s “README first” philosophy   |
| LLM Runtime | [Ollama](https://ollama.ai)                      |
| GUI Toolkit | [Qt 6](https://www.qt.io) via PyQt6              |
| Badges      | [Shields.io](https://shields.io)                 |
| Icons       | [HeroIcons](https://heroicons.com)               |
| Maintainer  | [@LikithMeruvu](https://github.com/LikithMeruvu) |

<p align="center"><i>Clipboard AI – because copy‑paste deserves super‑powers.</i></p>
```

---

### References

* README structure & badge guidelines ([GitHub][1], [GitHub Docs][2], [Open Source Guides][3], [Shields.io | Shields.io][4])
* Qt system‑tray & clipboard classes underpin tray/monitor design ([Qt Documentation][5], [Qt Documentation][6])
* PyInstaller & cross‑platform packaging guidance ([Python GUIs][7])
* Ollama local LLM API & OpenAI compatibility used for on‑device inference ([Ollama][8])
* Gemma 3 and DeepSeek model metadata for default model choices ([Ollama][9], [Ollama][10])
* `keyboard` & global hot‑keys library capabilities inspiring key‑binding section ([PyPI][11])
* `appdirs` best‑practice for per‑user config location ([PyPI][12])
* MIT licence overview ([PyPI][12])

[1]: https://github.com/jehna/readme-best-practices?utm_source=chatgpt.com "GitHub - jehna/readme-best-practices: Best practices for writing a ..."
[2]: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax?utm_source=chatgpt.com "Basic writing and formatting syntax - GitHub Docs"
[3]: https://opensource.guide/how-to-contribute/?utm_source=chatgpt.com "How to Contribute to Open Source"
[4]: https://shields.io/?utm_source=chatgpt.com "Shields.io | Shields.io"
[5]: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QSystemTrayIcon.html?utm_source=chatgpt.com "PySide6.QtWidgets.QSystemTrayIcon - Qt for Python"
[6]: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QClipboard.html?utm_source=chatgpt.com "PySide6.QtGui.QClipboard - Qt for Python"
[7]: https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/?utm_source=chatgpt.com "Packaging PyQt5 applications for Windows with PyInstaller & InstallForge"
[8]: https://registry.ollama.ai/blog/openai-compatibility?utm_source=chatgpt.com "OpenAI compatibility · Ollama Blog"
[9]: https://registry.ollama.ai/library/gemma3/blobs/aeda25e63ebd?utm_source=chatgpt.com "gemma3/model - registry.ollama.ai"
[10]: https://registry.ollama.ai/library/deepseek-r1/blobs/96c415656d37?utm_source=chatgpt.com "deepseek-r1/model - registry.ollama.ai"
[11]: https://pypi.org/project/keyboard/?utm_source=chatgpt.com "keyboard - PyPI"
[12]: https://pypi.org/project/appdirs/?utm_source=chatgpt.com "appdirs - PyPI"
