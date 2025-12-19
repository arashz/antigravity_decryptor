# Antigravity Decryptor

A standalone, portable tool to decrypt and extract human-readable conversations from Antigravity IDE's encrypted `.pb` conversation files.

> 🚀 **New user?** Check out the [Quick Start Guide](QUICKSTART.md) to get started in 2 minutes!

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| 🚀 [Quick Start](QUICKSTART.md) | Get started in 2 minutes |
| 📖 [API Reference](API_REFERENCE.md) | Complete API documentation for developers |
| 🔍 [Analyzing Conversations](ANALYZING_CONVERSATIONS.md) | Guide to understanding and analyzing your conversations |
| 🔐 [Understanding the Format](UNDERSTANDING_THE_FORMAT.md) | Deep dive into file format and encryption |
| ❓ [FAQ](FAQ.md) | Frequently asked questions |
| 🐛 [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| 🤝 [Contributing](CONTRIBUTING.md) | How to contribute to the project |

## Quick Start

```bash
# Option 1: Install as a package (recommended)
pip install -e .

# Option 2: Install dependencies only
pip install -r requirements.txt

# Decrypt a conversation file
python antigravity_decrypt.py conversation.pb --output conversation.json

# Interactive mode (great for beginners!)
python antigravity_decrypt.py --interactive

# Decrypt all files in a directory with progress tracking
python antigravity_decrypt.py ./conversations --output ./decrypted
```

## Features

- ✅ **Standalone**: Single script, no external dependencies beyond standard libraries
- ✅ **Portable**: Works on any system with Python 3.6+
- ✅ **Multiple key sources**: Keychain (macOS), environment variable, or command-line argument
- ✅ **Batch processing**: Process single files or entire directories with progress tracking
- ✅ **Multiple output formats**: JSON or human-readable text
- ✅ **Automatic extraction**: Extracts conversation messages from protobuf structure
- ✨ **Interactive mode**: Step-by-step prompts for beginners
- ✨ **Beautiful CLI**: Colored output, progress bars, and helpful error messages
- ✨ **Pip installable**: Install as a package with `pip install`
- ✨ **Rich examples**: Practical examples for common use cases

## Installation

### Option 1: Install as a Package (Recommended)

```bash
# Clone the repository
git clone https://github.com/arashz/antigravity_decryptor.git
cd antigravity_decryptor

# Install in editable mode
pip install -e .

# Now you can use it anywhere!
antigravity-decrypt --help
```

### Option 2: Direct Script Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Use the script directly
python antigravity_decrypt.py --help
```

### Option 3: Dependencies Only

```bash
pip install cryptography protobuf
```

## Usage

### Interactive Mode (Easiest!)

Perfect for first-time users:

```bash
# Launch interactive mode with step-by-step prompts
python antigravity_decrypt.py --interactive

# Or just run without arguments
python antigravity_decrypt.py
```

The interactive mode will guide you through:
1. Selecting input file/directory
2. Providing encryption key
3. Choosing output location
4. Selecting output format

### Basic Usage

```bash
# Decrypt a single file (outputs to stdout as JSON)
python antigravity_decrypt.py conversation.pb

# Decrypt and save to file
python antigravity_decrypt.py conversation.pb --output conversation.json

# Decrypt as human-readable text
python antigravity_decrypt.py conversation.pb --format text --output conversation.txt

# Decrypt all files in a directory (with progress bar!)
python antigravity_decrypt.py ./conversations --output ./decrypted

# Show version
python antigravity_decrypt.py --version
```

### Key Management

The script tries to get the encryption key in this order:

1. **Command-line argument** (highest priority):
   ```bash
   python antigravity_decrypt.py conversation.pb --key "qFl7rbZfqbZoahxeyCwdCg=="
   ```

2. **Environment variable**:
   ```bash
   export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
   python antigravity_decrypt.py conversation.pb
   ```

3. **macOS Keychain** (automatic on macOS):
   - Service: `Antigravity Safe Storage`
   - Account: `Antigravity Key`

### Output Formats

**JSON Format** (default):
```json
{
  "file": "conversation.pb",
  "success": true,
  "messages": [
    {
      "content": "Message text here...",
      "length": 123
    }
  ],
  "metadata": {
    "size": 172850,
    "decrypted_size": 172832,
    "field_count": 4,
    "message_count": 15
  }
}
```

**Text Format**:
```
File: conversation.pb
Status: Success
Messages: 15

======================================================================
CONVERSATION CONTENT
======================================================================

--- Message 1 (123 chars) ---
Message text here...

--- Message 2 (456 chars) ---
Another message...
```

## Examples

### Extract conversations from Antigravity IDE

```bash
# On macOS (keychain access)
python antigravity_decrypt.py ~/.gemini/antigravity/conversations/ --output ./my_conversations

# On other systems (with key)
python antigravity_decrypt.py conversations/ --key "YOUR_KEY_HERE" --output ./decrypted

# With verbose output for debugging
python antigravity_decrypt.py conversations/ --verbose
```

### Process and analyze

```bash
# Get all conversations as JSON with progress tracking
python antigravity_decrypt.py conversations/ --output ./decrypted --format json

# Then analyze with jq
cat ./decrypted/summary.json | jq '.files[] | select(.success) | {file: .file, messages: .metadata.message_count}'
```

### Practical Examples

Check out the `examples/` directory for complete, ready-to-use examples:

- **`basic_usage.sh`**: Quick reference for common commands
- **`batch_process.py`**: Programmatic batch processing with Python API
- **`analyze_conversations.py`**: Advanced analysis with statistics and search

```bash
# View available examples
ls examples/

# Run the analysis example
python examples/analyze_conversations.py --input ./conversations --output report.json
```

See `examples/README.md` for detailed information about each example.

## Integration into Other Projects

### As a Python Module

```python
from antigravity_decrypt import decrypt_file, extract_conversation_messages, parse_protobuf_wire_format
import base64

# Get key
key = base64.b64decode("qFl7rbZfqbZoahxeyCwdCg==")

# Decrypt
decrypted = decrypt_file("conversation.pb", key)

# Parse
fields = parse_protobuf_wire_format(decrypted)

# Extract messages
messages = extract_conversation_messages(fields)

for msg in messages:
    print(msg['content'])
```

### As a Command-Line Tool

Simply copy `antigravity_decrypt.py` to your project and use it:

```bash
cp antigravity_decrypt.py /path/to/your/project/
cd /path/to/your/project/
python antigravity_decrypt.py conversations/ --output decrypted/
```

## Technical Details

### Encryption Method
- **Algorithm**: AES-128-CTR (Counter Mode)
- **Key Size**: 16 bytes (128 bits)
- **Nonce/IV**: First 16 bytes of encrypted file

### File Format
- Files are encrypted Protocol Buffer (protobuf) format
- Some files may have header bytes (0-4 bytes) that need to be skipped
- After decryption, some files may need 0-4 bytes skipped to align with protobuf structure

### Protobuf Parsing
- Uses wire format parsing (no schema required)
- Recursively extracts nested messages
- Automatically detects and decodes UTF-8 strings

## Need Help?

### 📚 Comprehensive Documentation

We've created extensive guides to help you:

- **🚀 [Quick Start Guide](QUICKSTART.md)** - Get up and running in 2 minutes
- **📖 [API Reference](API_REFERENCE.md)** - Complete Python API documentation with examples
- **🔍 [Analyzing Conversations](ANALYZING_CONVERSATIONS.md)** - Learn how to extract insights from your conversations
- **🔐 [Understanding the Format](UNDERSTANDING_THE_FORMAT.md)** - Technical deep-dive into encryption and file structure
- **❓ [FAQ](FAQ.md)** - Answers to frequently asked questions
- **🐛 [Troubleshooting Guide](TROUBLESHOOTING.md)** - Detailed solutions to common issues

### Troubleshooting

Having issues? Check out the [comprehensive troubleshooting guide](TROUBLESHOOTING.md) for detailed solutions.

### Quick Fixes

**"Could not retrieve encryption key"**
- Provide key via `--key` argument or `ANTIGRAVITY_KEY` environment variable
- On macOS, ensure keychain access is granted

**"Decryption failed"**
- Verify the key is correct (base64 encoded)
- Check that the file is actually an Antigravity conversation file
- Try with `--verbose` flag for more details

**"Could not parse protobuf"**
- File may be corrupted
- File may use a different encryption method (unlikely)
- Try decrypting with different skip amounts manually

**"No .pb files found"**
- Check directory path is correct
- Verify files have `.pb` extension
- Use absolute paths if needed

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub.

## Author

Arash Zolfaghari

## License

This script is provided as-is for educational and personal use. Use responsibly and in accordance with applicable laws and terms of service.

