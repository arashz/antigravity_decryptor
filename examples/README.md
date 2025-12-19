# Antigravity Decryptor - Examples

This directory contains practical examples for using the Antigravity Decryptor.

## 📁 Files

### `basic_usage.sh`
Quick reference guide showing common command-line usage patterns:
- Single file decryption
- Batch directory processing
- Different output formats
- Interactive mode
- Environment variable usage

**Usage:**
```bash
chmod +x basic_usage.sh
./basic_usage.sh
```

### `batch_process.py`
Python script demonstrating programmatic usage:
- Batch processing multiple files
- Using the Python API directly
- Custom message handling
- Error handling patterns

**Usage:**
```bash
python batch_process.py
```

### `analyze_conversations.py`
Advanced example showing conversation analysis:
- Extract statistics from conversations
- Search for specific content
- Export in different formats
- Generate reports

**Usage:**
```bash
python analyze_conversations.py --input ./conversations --output report.json
```

## 🚀 Quick Start

### Command-Line Usage

```bash
# 1. Decrypt a single file
python ../antigravity_decrypt.py conversation.pb --key "YOUR_KEY" --output output.json

# 2. Interactive mode (easiest for beginners)
python ../antigravity_decrypt.py --interactive

# 3. Batch process directory
python ../antigravity_decrypt.py ./conversations --output ./decrypted

# 4. Human-readable text output
python ../antigravity_decrypt.py conversation.pb --format text --output conversation.txt
```

### Python API Usage

```python
import base64
from antigravity_decrypt import decrypt_file, extract_conversation_messages, parse_protobuf_wire_format

# Setup
key = base64.b64decode("YOUR_KEY_HERE")

# Decrypt
decrypted = decrypt_file("conversation.pb", key)

# Parse and extract
fields = parse_protobuf_wire_format(decrypted)
messages = extract_conversation_messages(fields)

# Use the messages
for msg in messages:
    print(msg['content'])
```

## 📚 Additional Resources

- **Main README**: See `../README.md` for comprehensive documentation
- **Installation**: `pip install antigravity-decryptor` or use directly
- **GitHub**: https://github.com/arashz/antigravity_decryptor

## 💡 Tips

1. **Keep your encryption key secure** - Never commit it to version control
2. **Use environment variables** for keys in scripts: `export ANTIGRAVITY_KEY="..."`
3. **Start with interactive mode** if you're new to the tool
4. **Use verbose mode** (`-v`) when troubleshooting issues
5. **Check summary.json** after batch processing for detailed results

## 🤝 Contributing

Have a useful example? Feel free to contribute by opening a pull request!
