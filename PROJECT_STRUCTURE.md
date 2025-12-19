# Project Structure

This is a standalone, portable tool for decrypting Antigravity IDE conversation files with a delightful developer experience.

## Core Files

- **`antigravity_decrypt.py`** - Main decryptor script with enhanced CLI (colors, progress bars, interactive mode)
- **`requirements.txt`** - Python dependencies (cryptography, protobuf)
- **`setup.py`** - Package setup for pip installation
- **`pyproject.toml`** - Modern Python package configuration

## Documentation

### Main Documentation
- **`README.md`** - Main documentation and usage guide
- **`DOCS_INDEX.md`** - Complete documentation navigation guide
- **`QUICKSTART.md`** - 2-minute quick start guide for new users

### Developer Documentation
- **`API_REFERENCE.md`** - Complete Python API reference with examples
- **`ANALYZING_CONVERSATIONS.md`** - Guide to analyzing and extracting insights
- **`UNDERSTANDING_THE_FORMAT.md`** - Technical deep-dive into file format and encryption

### Support Documentation
- **`FAQ.md`** - Frequently asked questions with quick answers
- **`TROUBLESHOOTING.md`** - Detailed troubleshooting guide with solutions

### Project Documentation
- **`CONTRIBUTING.md`** - Guidelines for contributors
- **`CHANGELOG.md`** - Version history and release notes
- **`IMPROVEMENTS_SUMMARY.md`** - Summary of recent improvements
- **`PROJECT_STRUCTURE.md`** - This file
- **`LICENSE`** - MIT License

## Examples

- **`examples/README.md`** - Overview of all examples
- **`examples/basic_usage.sh`** - Quick command reference
- **`examples/batch_process.py`** - Python API usage examples
- **`examples/analyze_conversations.py`** - Advanced conversation analysis tool

## Configuration

- **`.gitignore`** - Git ignore rules (excludes decrypted files, keys, build artifacts)
- **`.antigravity_config.example`** - Example configuration file for power users

## Features by Version

### v1.1.0 (Current)
- 🎨 Interactive mode with step-by-step prompts
- 🌈 Colored terminal output with emojis
- 📊 Progress bars for batch processing
- 📦 Pip installable package
- 📁 Comprehensive examples
- ✨ Enhanced error messages
- 🚀 Better user experience throughout

### v1.0.0
- AES-CTR, AES-CBC, and AES-GCM decryption
- macOS Keychain integration
- JSON and text output formats
- Batch processing
- Protobuf parsing

## Dependencies

- Python 3.6+
- `cryptography>=41.0.0` - For AES decryption
- `protobuf>=4.24.0` - For parsing protobuf wire format

## Installation Options

1. **As a package:** `pip install -e .`
2. **Direct script:** `pip install -r requirements.txt`
3. **Dependencies only:** `pip install cryptography protobuf`

## Usage

See documentation for complete usage instructions:
- Quick start: `QUICKSTART.md`
- Full guide: `README.md`
- Examples: `examples/README.md`
- Troubleshooting: `TROUBLESHOOTING.md`

## Standalone

This project contains everything needed to decrypt Antigravity conversation files. No other files or directories from external sources are required.

