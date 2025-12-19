# Antigravity Decryptor (Node.js Version)

A standalone, portable Node.js tool to decrypt and extract human-readable conversations from Antigravity IDE's encrypted `.pb` conversation files.

This is the Node.js version of the [Python Antigravity Decryptor](../README.md). Both versions provide the same functionality.

## Quick Start

```bash
# Install dependencies
npm install

# Decrypt a conversation file
node antigravity-decrypt.js conversation.pb --output conversation.json

# Interactive mode (great for beginners!)
node antigravity-decrypt.js --interactive

# Decrypt all files in a directory with progress tracking
node antigravity-decrypt.js ./conversations --output ./decrypted
```

## Features

- ✅ **Standalone**: Single script, minimal dependencies
- ✅ **Portable**: Works on any system with Node.js 14+
- ✅ **Multiple key sources**: Keychain (macOS), environment variable, or command-line argument
- ✅ **Batch processing**: Process single files or entire directories with progress tracking
- ✅ **Multiple output formats**: JSON or human-readable text
- ✅ **Automatic extraction**: Extracts conversation messages from protobuf structure
- ✨ **Interactive mode**: Step-by-step prompts for beginners
- ✨ **Beautiful CLI**: Colored output, progress bars, and helpful error messages
- ✨ **NPM installable**: Install globally or use locally

## Installation

### Option 1: Local Installation

```bash
# Clone the repository (if not already)
git clone https://github.com/arashz/antigravity_decryptor.git
cd antigravity_decryptor/node

# Install dependencies
npm install

# Use the script
node antigravity-decrypt.js --help
```

### Option 2: Global Installation

```bash
cd antigravity_decryptor/node
npm install -g .

# Now you can use it anywhere!
antigravity-decrypt --help
```

### Option 3: Direct Execution

Node.js has all required modules built-in, so no dependencies are needed:

```bash
# Run directly without any installation
node antigravity-decrypt.js conversation.pb --key "YOUR_KEY"
```

## Usage

### Interactive Mode (Easiest!)

Perfect for first-time users:

```bash
# Launch interactive mode with step-by-step prompts
node antigravity-decrypt.js --interactive

# Or just run without arguments
node antigravity-decrypt.js
```

The interactive mode will guide you through:
1. Selecting input file/directory
2. Providing encryption key
3. Choosing output location
4. Selecting output format

### Basic Usage

```bash
# Decrypt a single file (outputs to stdout as JSON)
node antigravity-decrypt.js conversation.pb

# Decrypt and save to file
node antigravity-decrypt.js conversation.pb --output conversation.json

# Decrypt as human-readable text
node antigravity-decrypt.js conversation.pb --format text --output conversation.txt

# Decrypt all files in a directory (with progress bar!)
node antigravity-decrypt.js ./conversations --output ./decrypted

# Show version
node antigravity-decrypt.js --version
```

### Key Management

The script tries to get the encryption key in this order:

1. **Command-line argument** (highest priority):
   ```bash
   node antigravity-decrypt.js conversation.pb --key "qFl7rbZfqbZoahxeyCwdCg=="
   ```

2. **Environment variable**:
   ```bash
   export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
   node antigravity-decrypt.js conversation.pb
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
node antigravity-decrypt.js ~/.gemini/antigravity/conversations/ --output ./my_conversations

# On other systems (with key)
node antigravity-decrypt.js conversations/ --key "YOUR_KEY_HERE" --output ./decrypted

# With verbose output for debugging
node antigravity-decrypt.js conversations/ --verbose
```

### Process and analyze

```bash
# Get all conversations as JSON with progress tracking
node antigravity-decrypt.js conversations/ --output ./decrypted --format json

# Then analyze with jq
cat ./decrypted/summary.json | jq '.files[] | select(.success) | {file: .file, messages: .metadata.message_count}'
```

### Example Scripts

See the `examples/` directory for complete examples:

- **`basic-usage.js`**: Programmatic usage examples demonstrating single file processing, batch operations, and key management

## Integration into Other Projects

### As a Node.js Module

```javascript
const { decryptFile, processConversationFile, extractConversationMessages } = require('./antigravity-decrypt');

// Get key
const key = Buffer.from('qFl7rbZfqbZoahxeyCwdCg==', 'base64');

// Decrypt and process
const result = processConversationFile('conversation.pb', key);

if (result.success) {
  result.messages.forEach(msg => {
    console.log(msg.content);
  });
}
```

### As a Command-Line Tool

Simply copy `antigravity-decrypt.js` to your project and use it:

```bash
cp antigravity-decrypt.js /path/to/your/project/
cd /path/to/your/project/
node antigravity-decrypt.js conversations/ --output decrypted/
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

## Troubleshooting

### Common Issues

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

**"No .pb files found"**
- Check directory path is correct
- Verify files have `.pb` extension
- Use absolute paths if needed

## Requirements

- Node.js 16.0.0 or higher
- No external dependencies required (uses built-in Node.js crypto module)

## Comparison with Python Version

Both versions provide the same functionality. Choose based on your preference:

| Feature | Python Version | Node.js Version |
|---------|---------------|-----------------|
| Installation | `pip install -e .` | No installation needed |
| Dependencies | cryptography, protobuf | None (built-in only) |
| Performance | Fast | Fast |
| Platform Support | Python 3.6+ | Node.js 16+ |
| CLI Features | ✅ All features | ✅ All features |

## Author

Arash Zolfaghari

## License

This script is provided as-is for educational and personal use. Use responsibly and in accordance with applicable laws and terms of service.
