# Changelog

## [1.1.0] - 2025-12-19

### Added
- 🎨 **Interactive mode** with step-by-step prompts for beginners
- 🌈 **Colored terminal output** with emojis for better user experience
- 📊 **Progress bars** for batch processing operations
- ✨ **Version flag** (`--version`) to display current version
- 📦 **Package installation support** via setup.py and pyproject.toml
- 📁 **Comprehensive examples** directory with practical usage examples
- 🔍 **Advanced analysis example** with statistics and keyword search
- 📖 **Enhanced documentation** with better examples and guides

### Improved
- 💬 **Better error messages** with actionable suggestions
- 🎯 **Improved CLI help** with colored examples and tips
- 📈 **Enhanced batch processing output** with detailed summaries
- 🚀 **Better user feedback** throughout the decryption process

### Examples Added
- `basic_usage.sh`: Quick command reference
- `batch_process.py`: Python API usage examples
- `analyze_conversations.py`: Advanced conversation analysis tool
- `examples/README.md`: Comprehensive examples documentation

## [1.0.0] - 2025-12-19

### Added
- Initial release of Antigravity IDE conversation decryptor
- Support for AES-CTR, AES-CBC, and AES-GCM decryption methods
- Automatic key retrieval from macOS Keychain
- Support for environment variable and command-line key input
- JSON and text output formats
- Batch processing for directories
- Automatic protobuf parsing and text extraction
- Flexible skip detection for file format variations

### Features
- Decrypts encrypted `.pb` conversation files
- Extracts human-readable conversation messages
- Handles multiple encryption methods with automatic fallback
- Portable and standalone (no external dependencies beyond standard libraries)

