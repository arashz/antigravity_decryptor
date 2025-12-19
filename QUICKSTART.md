# 🚀 Quick Start Guide

Get up and running with Antigravity Decryptor in 2 minutes!

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Step 1: Installation

Choose your preferred method:

### 📦 Method A: Install as Package (Recommended)

```bash
git clone https://github.com/arashz/antigravity_decryptor.git
cd antigravity_decryptor
pip install -e .
```

Now you can use `antigravity-decrypt` from anywhere!

### 📄 Method B: Direct Script Usage

```bash
git clone https://github.com/arashz/antigravity_decryptor.git
cd antigravity_decryptor
pip install -r requirements.txt
```

Use with `python antigravity_decrypt.py`

## Step 2: Get Your Encryption Key

You need the encryption key to decrypt files. You have three options:

### Option 1: macOS Keychain (macOS only)
If you're on macOS, the key is automatically retrieved from Keychain!

### Option 2: Environment Variable
```bash
export ANTIGRAVITY_KEY="YOUR_BASE64_KEY_HERE"
```

### Option 3: Command-line Argument
```bash
--key "YOUR_BASE64_KEY_HERE"
```

## Step 3: Decrypt Your First File

### 🎯 Interactive Mode (Easiest!)

Perfect for first-time users:

```bash
python antigravity_decrypt.py --interactive
```

Just follow the prompts!

### 📝 Command Line

```bash
# Decrypt a single file
python antigravity_decrypt.py conversation.pb --output conversation.json

# Decrypt a directory (with cool progress bar!)
python antigravity_decrypt.py ./conversations --output ./decrypted
```

## Step 4: View Results

### JSON Output
```bash
cat conversation.json | python -m json.tool
# Or use jq for better formatting:
cat conversation.json | jq '.'
```

### Text Output
```bash
# Get human-readable text
python antigravity_decrypt.py conversation.pb --format text --output conversation.txt
cat conversation.txt
```

## Common Use Cases

### 🔍 Extract conversations from Antigravity IDE

```bash
# On macOS (automatic key retrieval)
python antigravity_decrypt.py ~/.gemini/antigravity/conversations/ --output ./my_conversations

# On other systems
python antigravity_decrypt.py conversations/ --key "YOUR_KEY" --output ./decrypted
```

### 📊 Analyze conversations

```bash
# Use the analysis example
python examples/analyze_conversations.py --input ./conversations --output report.json
```

### 🔄 Batch process with custom logic

```bash
# Use the Python API
python examples/batch_process.py
```

## Troubleshooting

### "Could not retrieve encryption key"

**Solution:** Provide the key using one of these methods:
```bash
# Method 1: Command-line
python antigravity_decrypt.py file.pb --key "YOUR_KEY"

# Method 2: Environment variable
export ANTIGRAVITY_KEY="YOUR_KEY"
python antigravity_decrypt.py file.pb
```

### "No .pb files found"

**Solution:** Make sure you're pointing to the correct directory:
```bash
# Check directory contents
ls -la /path/to/conversations/

# Use absolute path if needed
python antigravity_decrypt.py /absolute/path/to/conversations/
```

### "Decryption failed"

**Solutions:**
1. Verify your key is correct
2. Make sure the file is actually an Antigravity conversation file
3. Try with verbose mode: `--verbose` to see more details

## Next Steps

- 📖 Read the [full README](README.md) for comprehensive documentation
- 💡 Check out [examples](examples/) for advanced usage
- 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- 🐛 Found a bug? [Open an issue](https://github.com/arashz/antigravity_decryptor/issues)

## Need Help?

- Check `--help`: `python antigravity_decrypt.py --help`
- Read the [full documentation](README.md)
- Open an issue on GitHub

---

**Happy decrypting! 🎉**
