# ❓ Frequently Asked Questions (FAQ)

Quick answers to common questions about Antigravity Decryptor.

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Usage & Features](#usage--features)
- [Security & Privacy](#security--privacy)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

---

## General Questions

### What is Antigravity Decryptor?

Antigravity Decryptor is a tool that decrypts and extracts human-readable conversations from Antigravity IDE's encrypted `.pb` (Protocol Buffer) files.

**Key features:**
- ✅ Standalone Python script
- ✅ Multiple encryption method support
- ✅ Batch processing
- ✅ Beautiful CLI with colors and progress bars
- ✅ Interactive mode for beginners

### Why would I need this?

You might want to:
- 📚 **Analyze your conversations** for learning purposes
- 🔍 **Search through old conversations** for specific information
- 📊 **Extract code examples** for documentation
- 🗄️ **Archive conversations** in readable format
- 📈 **Analyze conversation patterns** and statistics

### Is this legal and safe to use?

**Yes!** This tool:
- ✅ Only works on your own files
- ✅ Uses your own encryption key
- ✅ Runs locally on your machine
- ✅ Doesn't send data anywhere

**However:**
- ⚠️ Respect terms of service
- ⚠️ Use responsibly
- ⚠️ Keep decrypted data secure

---

## Installation & Setup

### What do I need to run this tool?

**Requirements:**
- Python 3.6 or higher
- Two Python packages: `cryptography` and `protobuf`
- Your encryption key

**Installation:**
```bash
# Option 1: Install as package
pip install -e .

# Option 2: Install dependencies only
pip install cryptography protobuf
```

### How do I get my encryption key?

**On macOS:**
The tool automatically retrieves the key from your Keychain! No manual action needed.

**On other systems:**
1. Set as environment variable:
   ```bash
   export ANTIGRAVITY_KEY="YOUR_KEY_HERE"
   ```

2. Or pass via command-line:
   ```bash
   python antigravity_decrypt.py file.pb --key "YOUR_KEY_HERE"
   ```

### Where do I find my conversation files?

**Common locations:**

**macOS:**
```
~/.gemini/antigravity/conversations/
~/Library/Application Support/Antigravity/conversations/
```

**Linux:**
```
~/.config/antigravity/conversations/
~/.local/share/antigravity/conversations/
```

**Windows:**
```
%APPDATA%\Antigravity\conversations\
%LOCALAPPDATA%\Antigravity\conversations\
```

**Search command:**
```bash
find ~ -name "*.pb" -path "*/antigravity/*" 2>/dev/null
```

### Do I need to install anything else?

**No!** The tool only needs:
- Python 3.6+
- `cryptography` package
- `protobuf` package

Everything else is built-in.

---

## Usage & Features

### What's the easiest way to use this tool?

**Interactive mode!**

```bash
python antigravity_decrypt.py --interactive
```

It will guide you step-by-step through:
1. Selecting your file/directory
2. Providing the encryption key
3. Choosing output location
4. Selecting output format

### Can I decrypt multiple files at once?

**Yes!** Use directory mode:

```bash
# Decrypt all .pb files in a directory
python antigravity_decrypt.py ./conversations --output ./decrypted
```

You'll get:
- 📊 Progress bar showing status
- 📁 All files decrypted to output directory
- 📄 Summary file with statistics

### What output formats are available?

**Two formats:**

**1. JSON (default)** - Machine-readable
```bash
python antigravity_decrypt.py file.pb --output output.json
```

**2. Text** - Human-readable
```bash
python antigravity_decrypt.py file.pb --format text --output output.txt
```

### Can I use this in my Python scripts?

**Absolutely!** Import and use directly:

```python
from antigravity_decrypt import process_conversation_file
import base64

key = base64.b64decode("YOUR_KEY")
result = process_conversation_file("conversation.pb", key)

for msg in result['messages']:
    print(msg['content'])
```

See [API Reference](API_REFERENCE.md) for complete documentation.

### How do I search for specific content?

**Method 1: Using the analysis example**
```bash
python examples/analyze_conversations.py --input ./conversations --search "keyword"
```

**Method 2: Using command-line tools**
```bash
# Decrypt to JSON
python antigravity_decrypt.py conversations/ --output decrypted/

# Search with grep
grep -r "search term" decrypted/

# Search with jq
find decrypted/ -name "*.json" -exec jq '.messages[] | select(.content | contains("keyword"))' {} \;
```

**Method 3: Python script**
```python
result = process_conversation_file(file, key)
matches = [m for m in result['messages'] if 'keyword' in m['content'].lower()]
```

---

## Security & Privacy

### Is my encryption key safe?

**Key security depends on how you store it:**

✅ **Safe:**
- macOS Keychain (automatic)
- Environment variable (not committed to git)
- Command-line argument (in private terminal)

❌ **Unsafe:**
- Hardcoded in scripts
- Committed to version control
- Shared in public places

**Best practice:**
```bash
# Use environment variable
export ANTIGRAVITY_KEY="YOUR_KEY"

# Or let macOS Keychain handle it automatically
```

### Will this tool send my data anywhere?

**NO!** The tool:
- ✅ Runs completely locally
- ✅ Doesn't make network requests
- ✅ Doesn't upload data anywhere
- ✅ Is fully open source (you can verify!)

### Should I share my decrypted conversations?

**Be careful!** Decrypted conversations may contain:
- 🔒 Proprietary code
- 🔒 Sensitive information
- 🔒 Personal details
- 🔒 API keys or credentials

**Before sharing:**
1. Review content thoroughly
2. Remove sensitive information
3. Consider privacy implications
4. Get consent if conversations involve others

### How do I securely delete decrypted files?

**On Unix/Linux/macOS:**
```bash
# Secure delete (if available)
shred -vfz -n 10 decrypted_file.json

# Or use rm (less secure)
rm decrypted_file.json
```

**On all systems:**
```bash
# Delete directory
rm -rf ./decrypted/

# Clear from trash (macOS)
rm -rf ~/.Trash/*
```

---

## Troubleshooting

### "Could not retrieve encryption key" - What do I do?

**Solutions in order:**

1. **Provide key via command-line:**
   ```bash
   python antigravity_decrypt.py file.pb --key "YOUR_KEY"
   ```

2. **Set environment variable:**
   ```bash
   export ANTIGRAVITY_KEY="YOUR_KEY"
   python antigravity_decrypt.py file.pb
   ```

3. **macOS users:** Check Keychain Access
   - Open Keychain Access app
   - Search for "Antigravity Safe Storage"
   - Grant access if prompted

See [Troubleshooting Guide](TROUBLESHOOTING.md#encryption-key-issues) for more details.

### "Decryption failed" - What's wrong?

**Common causes:**

1. **Wrong key**
   - Verify your key is correct
   - Try with a different file to test

2. **Corrupted file**
   - Check file size: `ls -lh file.pb`
   - Try with a different file

3. **Not an Antigravity file**
   - Verify file is actually from Antigravity IDE
   - Check file extension is `.pb`

**Debugging steps:**
```bash
# Try with verbose mode
python antigravity_decrypt.py file.pb --verbose

# Check file is binary
file file.pb

# Check first bytes
hexdump -C file.pb | head
```

### "No .pb files found" - Where are my files?

**Search for them:**
```bash
# macOS/Linux
find ~ -name "*.pb" -path "*/antigravity/*" 2>/dev/null

# Check common locations
ls ~/.gemini/antigravity/conversations/
ls ~/.config/antigravity/conversations/
```

**If still not found:**
- Verify Antigravity IDE is installed
- Check if conversations were saved
- Try searching entire home directory (may take time)

### The tool is slow - How can I speed it up?

**Tips for better performance:**

1. **Process fewer files:**
   ```bash
   # Process specific file
   python antigravity_decrypt.py specific_file.pb
   ```

2. **Use faster storage:**
   - SSD is much faster than HDD
   - Local is faster than network drives

3. **Close other applications:**
   - Free up CPU and memory
   - Close intensive applications

4. **Process in batches:**
   ```bash
   # Process 10 files at a time
   ls conversations/*.pb | head -10 | xargs -I {} python antigravity_decrypt.py {}
   ```

**Note:** Decryption is CPU-intensive and takes time for large files.

### Colors don't work in my terminal - How do I fix it?

**Automatic detection:** Colors are automatically disabled in non-TTY environments.

**If colors appear as weird characters:**
```bash
# Disable colors explicitly
python antigravity_decrypt.py file.pb --no-color  # (if supported)

# Or redirect to file (colors auto-disable)
python antigravity_decrypt.py file.pb > output.json
```

---

## Advanced Topics

### Can I modify the decryption logic?

**Yes!** The tool is open source. You can:

1. **Fork the repository**
2. **Modify `antigravity_decrypt.py`**
3. **Test your changes**
4. **Submit a pull request** (optional)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How do I integrate this with other tools?

**Examples:**

**1. With jq (JSON processor):**
```bash
python antigravity_decrypt.py file.pb | jq '.messages[] | .content'
```

**2. With grep:**
```bash
python antigravity_decrypt.py file.pb --format text | grep "search term"
```

**3. With Python pandas:**
```python
import pandas as pd
result = process_conversation_file(file, key)
df = pd.DataFrame(result['messages'])
print(df.describe())
```

**4. With a database:**
```python
import sqlite3

conn = sqlite3.connect('conversations.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY,
        file TEXT,
        content TEXT,
        length INTEGER
    )
''')

result = process_conversation_file(file, key)
for msg in result['messages']:
    cursor.execute('INSERT INTO messages (file, content, length) VALUES (?, ?, ?)',
                   (result['file'], msg['content'], msg['length']))

conn.commit()
```

### Can I decrypt files from a different version of Antigravity IDE?

**Maybe!** The tool attempts multiple decryption methods and should work with:
- Different Antigravity IDE versions
- Different encryption configurations
- Different file format variations

**If it doesn't work:**
1. Try with `--verbose` to see what's failing
2. Open an issue on GitHub with details
3. Check if file format has changed significantly

### How do I contribute to this project?

**We welcome contributions!**

1. **Report bugs:** Open an issue on GitHub
2. **Suggest features:** Open an issue with enhancement tag
3. **Improve docs:** Submit a pull request
4. **Add examples:** Share your use cases
5. **Fix bugs:** Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### What if I have a question not covered here?

**Resources:**

1. **Documentation:**
   - [README.md](README.md) - General documentation
   - [QUICKSTART.md](QUICKSTART.md) - Getting started
   - [API Reference](API_REFERENCE.md) - API documentation
   - [Analyzing Conversations](ANALYZING_CONVERSATIONS.md) - Analysis guide
   - [Understanding the Format](UNDERSTANDING_THE_FORMAT.md) - Technical details
   - [Troubleshooting](TROUBLESHOOTING.md) - Common issues

2. **Get Help:**
   - Check existing GitHub issues
   - Open a new issue
   - Include error messages and system info

3. **Community:**
   - Share your use cases
   - Help others with issues
   - Contribute examples

---

## Quick Reference

### Common Commands

```bash
# Interactive mode (easiest!)
python antigravity_decrypt.py --interactive

# Single file
python antigravity_decrypt.py conversation.pb --output output.json

# Directory (batch)
python antigravity_decrypt.py ./conversations --output ./decrypted

# Text format
python antigravity_decrypt.py file.pb --format text --output output.txt

# With key
python antigravity_decrypt.py file.pb --key "YOUR_KEY"

# Verbose mode
python antigravity_decrypt.py file.pb --verbose

# Version
python antigravity_decrypt.py --version

# Help
python antigravity_decrypt.py --help
```

### Common Paths

```bash
# macOS
~/.gemini/antigravity/conversations/

# Linux
~/.config/antigravity/conversations/

# Find files
find ~ -name "*.pb" -path "*/antigravity/*"
```

### Environment Variable

```bash
# Set key
export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="

# Verify
echo $ANTIGRAVITY_KEY

# Use
python antigravity_decrypt.py file.pb
```

---

## Still Have Questions?

1. 📖 Check the [comprehensive documentation](README.md)
2. 🔍 Search [existing issues](https://github.com/arashz/antigravity_decryptor/issues)
3. 💬 Open a [new issue](https://github.com/arashz/antigravity_decryptor/issues/new)

**We're here to help! 🚀**
