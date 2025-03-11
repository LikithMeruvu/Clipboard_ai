from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clipboard_ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A desktop application that monitors the clipboard and processes content using Ollama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clipboard_ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.1",
        "requests>=2.31.0",
        "keyboard>=0.13.5",
        "python-dotenv>=1.0.0",
        "pyperclip>=1.8.2",
        "appdirs>=1.4.4",
    ],
    entry_points={
        "console_scripts": [
            "clipboard-ai=clipboard_ai:main",
        ],
    },
) 