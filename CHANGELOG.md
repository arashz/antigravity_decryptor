# Changelog

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

