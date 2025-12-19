# Antigravity Decryptor

A standalone, portable tool to decrypt and extract human-readable conversations from Antigravity IDE's encrypted `.pb` conversation files.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Decrypt a conversation file
python antigravity_decrypt.py conversation.pb --output conversation.json

# Decrypt all files in a directory
python antigravity_decrypt.py ./conversations --output ./decrypted
```

## Features

- ✅ **Standalone**: Single script, no external dependencies beyond standard libraries
- ✅ **Portable**: Works on any system with Python 3.6+
- ✅ **Multiple key sources**: Keychain (macOS), environment variable, or command-line argument
- ✅ **Batch processing**: Process single files or entire directories
- ✅ **Multiple output formats**: JSON or human-readable text
- ✅ **Automatic extraction**: Extracts conversation messages from protobuf structure

## Installation

```bash
pip install cryptography protobuf
```

## Usage

### Basic Usage

```bash
# Decrypt a single file (outputs to stdout as JSON)
python antigravity_decrypt.py conversation.pb

# Decrypt and save to file
python antigravity_decrypt.py conversation.pb --output conversation.json

# Decrypt as human-readable text
python antigravity_decrypt.py conversation.pb --format text --output conversation.txt

# Decrypt all files in a directory
python antigravity_decrypt.py ./conversations --output ./decrypted
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
```

### Process and analyze

```bash
# Get all conversations as JSON
python antigravity_decrypt.py conversations/ --output ./decrypted --format json

# Then analyze with jq
cat ./decrypted/summary.json | jq '.files[] | select(.success) | {file: .file, messages: .metadata.message_count}'
```

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

## Troubleshooting

### "Could not retrieve encryption key"
- Provide key via `--key` argument or `ANTIGRAVITY_KEY` environment variable
- On macOS, ensure keychain access is granted

### "Decryption failed"
- Verify the key is correct (base64 encoded)
- Check that the file is actually an Antigravity conversation file
- Try with `--verbose` flag for more details

### "Could not parse protobuf"
- File may be corrupted
- File may use a different encryption method (unlikely)
- Try decrypting with different skip amounts manually

## Author

Arash Zolfaghari

## License

This script is provided as-is for educational and personal use. Use responsibly and in accordance with applicable laws and terms of service.

