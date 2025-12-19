# Troubleshooting Guide

This guide helps you resolve common issues with Antigravity Decryptor.

## Installation Issues

### "cryptography library required"

**Problem:** Missing dependencies

**Solution:**
```bash
pip install cryptography protobuf
```

### "protobuf library required"

**Problem:** Missing protobuf package

**Solution:**
```bash
pip install protobuf
```

### Package installation fails

**Problem:** Outdated pip or setuptools

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install -e .
```

## Encryption Key Issues

### "Could not retrieve encryption key"

**Problem:** No encryption key provided

**Solutions:**

1. **Use command-line argument:**
   ```bash
   python antigravity_decrypt.py file.pb --key "YOUR_KEY"
   ```

2. **Set environment variable:**
   ```bash
   export ANTIGRAVITY_KEY="YOUR_KEY"
   python antigravity_decrypt.py file.pb
   ```

3. **macOS users:** Ensure keychain access is granted
   - Open Keychain Access app
   - Look for "Antigravity Safe Storage"
   - Grant access when prompted

### "Invalid key format"

**Problem:** Key is not base64 encoded

**Solution:** Ensure your key is properly base64 encoded. It should look like: `qFl7rbZfqbZoahxeyCwdCg==`

**How to encode a key:**
```python
import base64
key_bytes = b'your_16_byte_key'  # Must be 16 bytes for AES-128
key_b64 = base64.b64encode(key_bytes).decode('utf-8')
print(key_b64)
```

## Decryption Issues

### "Decryption failed"

**Possible causes and solutions:**

1. **Wrong key**
   - Verify you're using the correct encryption key
   - Try with verbose mode: `--verbose`

2. **Corrupted file**
   - Check file size: `ls -lh conversation.pb`
   - Try with a different file to verify your key works

3. **Not an Antigravity conversation file**
   - Ensure the file is actually from Antigravity IDE
   - Check file extension is `.pb`

4. **Different encryption method**
   - The tool tries multiple decryption methods automatically
   - If it still fails, the file may use an unsupported encryption

**Debug steps:**
```bash
# Try with verbose output
python antigravity_decrypt.py conversation.pb --key "YOUR_KEY" --verbose

# Check file contents (first few bytes)
hexdump -C conversation.pb | head
```

### "Could not parse protobuf"

**Problem:** Decryption succeeded but protobuf parsing failed

**Solutions:**

1. Try with verbose mode to see more details:
   ```bash
   python antigravity_decrypt.py conversation.pb --verbose
   ```

2. The file might be valid but not contain parseable protobuf data
   - This is rare but can happen with corrupted files

## File/Directory Issues

### "No .pb files found"

**Problem:** Directory doesn't contain .pb files

**Solutions:**

1. **Check directory contents:**
   ```bash
   ls -la /path/to/conversations/
   ```

2. **Use absolute path:**
   ```bash
   python antigravity_decrypt.py /absolute/path/to/conversations/
   ```

3. **Verify file extensions:**
   - Files must have `.pb` extension
   - Check for hidden files: `ls -a`

### "Permission denied"

**Problem:** No read/write permissions

**Solutions:**

1. **Check permissions:**
   ```bash
   ls -l conversation.pb
   ```

2. **Fix permissions:**
   ```bash
   chmod 644 conversation.pb
   ```

3. **Try a different output directory:**
   ```bash
   python antigravity_decrypt.py input.pb --output ~/Desktop/output.json
   ```

## Output Issues

### Output file is empty or incomplete

**Solutions:**

1. **Check if decryption was successful:**
   ```bash
   python antigravity_decrypt.py file.pb --verbose
   ```

2. **Try different output format:**
   ```bash
   # Try text format
   python antigravity_decrypt.py file.pb --format text --output output.txt
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

### JSON parsing errors when viewing output

**Problem:** Output JSON is malformed

**Solutions:**

1. **View with proper tool:**
   ```bash
   cat output.json | python -m json.tool
   # Or use jq
   cat output.json | jq '.'
   ```

2. **Regenerate output:**
   ```bash
   python antigravity_decrypt.py file.pb --output new_output.json
   ```

## Interactive Mode Issues

### Interactive mode hangs or doesn't respond

**Solutions:**

1. **Press Ctrl+C to exit**

2. **Try non-interactive mode:**
   ```bash
   python antigravity_decrypt.py file.pb --key "YOUR_KEY" --output output.json
   ```

3. **Check terminal compatibility:**
   - Some terminals may not support interactive input
   - Try a different terminal emulator

## Performance Issues

### Batch processing is slow

**Expected behavior:** Large files and many files take time

**Tips to improve:**

1. **Process fewer files at once:**
   ```bash
   # Process specific files
   python antigravity_decrypt.py specific_file.pb --output output.json
   ```

2. **Use verbose mode to see progress:**
   ```bash
   python antigravity_decrypt.py directory/ --verbose
   ```

3. **Check system resources:**
   ```bash
   # Monitor CPU and memory
   top
   ```

## macOS Keychain Issues

### "security command not found"

**Problem:** Not on macOS

**Solution:** Use `--key` argument or environment variable instead

### Keychain access denied

**Solutions:**

1. **Grant access in Keychain Access app**
   - Open Keychain Access
   - Find "Antigravity Safe Storage"
   - Double-click and grant access

2. **Use alternative key method:**
   ```bash
   python antigravity_decrypt.py file.pb --key "YOUR_KEY"
   ```

## Still Having Issues?

### Get More Information

1. **Run with verbose mode:**
   ```bash
   python antigravity_decrypt.py file.pb --verbose
   ```

2. **Check version:**
   ```bash
   python antigravity_decrypt.py --version
   ```

3. **Verify installation:**
   ```bash
   pip list | grep -E "cryptography|protobuf"
   ```

### Report a Bug

If you've tried everything and still have issues:

1. Open an issue on GitHub: https://github.com/arashz/antigravity_decryptor/issues
2. Include:
   - Your OS and Python version
   - The command you ran
   - Complete error message
   - Output from `--verbose` mode (remove sensitive information!)

### Get Help

- Check the [README](README.md) for comprehensive documentation
- See [QUICKSTART.md](QUICKSTART.md) for getting started
- Browse [examples/](examples/) for usage examples

---

**💡 Pro Tip:** Most issues can be resolved by using verbose mode (`--verbose`) to see what's happening!
