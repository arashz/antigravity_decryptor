# 📚 API Reference

Complete reference for using Antigravity Decryptor programmatically in your Python projects.

## Table of Contents

- [Installation](#installation)
- [Quick Example](#quick-example)
- [Core Functions](#core-functions)
- [Utility Functions](#utility-functions)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)

## Installation

```bash
pip install -e .
```

Or import directly:
```python
import sys
sys.path.insert(0, '/path/to/antigravity_decryptor')
from antigravity_decrypt import *
```

## Quick Example

```python
import base64
from antigravity_decrypt import process_conversation_file

# Your encryption key (base64 encoded)
key = base64.b64decode("YOUR_KEY_HERE")

# Process a conversation file
result = process_conversation_file("conversation.pb", key)

# Access the results
if result['success']:
    for msg in result['messages']:
        print(f"Message: {msg['content'][:100]}...")
        print(f"Length: {msg['length']} characters\n")
else:
    print(f"Error: {result['error']}")
```

## Core Functions

### `process_conversation_file(file_path, key, verbose=False)`

**High-level function to decrypt and process a conversation file in one call.**

**Parameters:**
- `file_path` (str): Path to the `.pb` conversation file
- `key` (bytes): 16-byte AES encryption key
- `verbose` (bool, optional): Enable verbose output. Default: `False`

**Returns:**
- `dict`: Result dictionary with structure:
  ```python
  {
      'file': str,           # Input file path
      'success': bool,       # Whether decryption succeeded
      'messages': list,      # List of extracted messages
      'metadata': dict,      # File metadata
      'error': str          # Error message (only if success=False)
  }
  ```

**Example:**
```python
result = process_conversation_file("chat.pb", key, verbose=True)
print(f"Found {len(result['messages'])} messages")
```

---

### `decrypt_file(file_path, key)`

**Decrypt an encrypted conversation file.**

Automatically tries multiple decryption methods (AES-CTR, AES-CBC, AES-GCM) and handles header/padding variations.

**Parameters:**
- `file_path` (str): Path to encrypted file
- `key` (bytes): 16-byte AES encryption key

**Returns:**
- `bytes`: Decrypted data, or `None` if decryption failed

**Example:**
```python
decrypted_data = decrypt_file("conversation.pb", key)
if decrypted_data:
    print(f"Decrypted {len(decrypted_data)} bytes")
```

**Note:** This function handles:
- Different encryption modes (CTR, CBC, GCM)
- Various skip amounts (0-4 bytes) for alignment
- File format variations

---

### `parse_protobuf_wire_format(data, max_depth=10, depth=0)`

**Parse protobuf wire format without a schema.**

Recursively extracts fields from Protocol Buffer binary data using wire format parsing.

**Parameters:**
- `data` (bytes): Decrypted protobuf data
- `max_depth` (int, optional): Maximum recursion depth. Default: `10`
- `depth` (int, optional): Current recursion depth (internal). Default: `0`

**Returns:**
- `list`: List of field dictionaries:
  ```python
  [
      {
          'field_number': int,
          'wire_type': int,
          'value': any,
          'interpreted_value': dict  # Human-readable interpretation
      },
      ...
  ]
  ```

**Example:**
```python
fields = parse_protobuf_wire_format(decrypted_data)
print(f"Found {len(fields)} top-level fields")

for field in fields:
    print(f"Field {field['field_number']}: {field['wire_type']}")
```

**Wire Types:**
- `0`: Varint (int, bool, enum)
- `1`: Fixed64 (double, fixed64)
- `2`: Length-delimited (string, bytes, nested message)
- `5`: Fixed32 (float, fixed32)

---

### `extract_conversation_messages(fields)`

**Extract human-readable messages from parsed protobuf fields.**

Intelligently extracts conversation content from the protobuf structure by identifying string fields that likely contain conversation text.

**Parameters:**
- `fields` (list): Parsed protobuf fields from `parse_protobuf_wire_format()`

**Returns:**
- `list`: List of message dictionaries:
  ```python
  [
      {
          'content': str,    # Message text
          'length': int      # Character count
      },
      ...
  ]
  ```

**Example:**
```python
fields = parse_protobuf_wire_format(decrypted_data)
messages = extract_conversation_messages(fields)

for i, msg in enumerate(messages, 1):
    print(f"Message {i}: {msg['content']}")
```

**Extraction Strategy:**
- Recursively searches nested structures
- Identifies text strings (UTF-8 encoded)
- Filters out short/empty strings
- Preserves message order

---

## Utility Functions

### `get_key_from_keychain()`

**Retrieve encryption key from macOS Keychain (macOS only).**

**Returns:**
- `bytes`: Encryption key, or `None` if retrieval failed

**Example:**
```python
key = get_key_from_keychain()
if key:
    print("Key retrieved from Keychain")
else:
    print("Failed to retrieve key from Keychain")
```

**Keychain Details:**
- Service: `Antigravity Safe Storage`
- Account: `Antigravity Key`
- Format: Base64 encoded

---

### `get_key_from_env()`

**Get encryption key from environment variable.**

**Returns:**
- `bytes`: Encryption key, or `None` if not found

**Example:**
```python
import os
os.environ['ANTIGRAVITY_KEY'] = 'qFl7rbZfqbZoahxeyCwdCg=='

key = get_key_from_env()
if key:
    print("Key retrieved from environment")
```

---

### Print Functions

Beautiful terminal output functions (automatically disabled in non-TTY environments):

```python
print_success(message)   # ✓ Green success message
print_error(message)     # ✗ Red error message  
print_warning(message)   # ⚠ Yellow warning message
print_info(message)      # ℹ Cyan info message
print_header(message)    # Bold cyan header
print_progress_bar(current, total, prefix='', suffix='', length=40)
```

**Example:**
```python
print_header("Processing Conversations")
print_info("Starting batch processing...")

for i in range(10):
    print_progress_bar(i+1, 10, prefix='Progress:', suffix='Complete')
    # ... process files ...

print_success("All files processed!")
```

---

## Data Structures

### Result Dictionary

Returned by `process_conversation_file()`:

```python
{
    # File information
    'file': 'conversation.pb',           # Input file path
    'success': True,                      # Success flag
    
    # Extracted messages
    'messages': [
        {
            'content': 'Full message text here...',
            'length': 1234                  # Character count
        },
        # ... more messages ...
    ],
    
    # Metadata about the file
    'metadata': {
        'size': 172850,                    # Original file size (bytes)
        'decrypted_size': 172832,          # Decrypted data size (bytes)
        'field_count': 4,                  # Number of protobuf fields
        'message_count': 15                # Number of messages extracted
    },
    
    # Error information (only if success=False)
    'error': 'Decryption failed: invalid key'
}
```

### Message Dictionary

Individual message structure:

```python
{
    'content': str,    # Full message text (UTF-8)
    'length': int      # Character count (len(content))
}
```

### Field Dictionary

Protobuf field structure from `parse_protobuf_wire_format()`:

```python
{
    'field_number': 1,                    # Protobuf field number
    'wire_type': 2,                       # Wire type (0-5)
    'value': b'raw bytes',                # Raw value
    'interpreted_value': {                # Human-readable interpretation
        'as_string': 'decoded text',      # UTF-8 decoded (if applicable)
        'length': 123,                    # Byte length
        'nested_fields': [...]            # Nested fields (if message type)
    }
}
```

---

## Error Handling

### Common Errors and Solutions

**KeyError / Invalid Key:**
```python
try:
    result = process_conversation_file(file_path, key)
    if not result['success']:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**File Not Found:**
```python
from pathlib import Path

file_path = "conversation.pb"
if not Path(file_path).exists():
    print(f"File not found: {file_path}")
else:
    result = process_conversation_file(file_path, key)
```

**Invalid Key Format:**
```python
import base64

try:
    key = base64.b64decode(key_string)
    if len(key) != 16:
        print("Key must be 16 bytes for AES-128")
except Exception as e:
    print(f"Invalid key format: {e}")
```

---

## Advanced Usage

### Batch Processing with Custom Logic

```python
from pathlib import Path
import base64

key = base64.b64decode("YOUR_KEY")
conversations_dir = Path("./conversations")

results = []
for pb_file in conversations_dir.glob("*.pb"):
    result = process_conversation_file(str(pb_file), key)
    results.append(result)
    
    if result['success']:
        # Custom processing
        messages = result['messages']
        
        # Filter messages by length
        long_messages = [m for m in messages if m['length'] > 500]
        print(f"{pb_file.name}: {len(long_messages)} long messages")

# Aggregate statistics
total_messages = sum(len(r['messages']) for r in results if r['success'])
print(f"Total: {total_messages} messages across {len(results)} files")
```

### Custom Decryption

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def custom_decrypt(encrypted_data, key):
    """Custom decryption with specific parameters."""
    # Extract IV (first 16 bytes)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CTR(iv),
        backend=default_backend()
    )
    
    # Decrypt
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# Use with parse_protobuf_wire_format
with open("conversation.pb", "rb") as f:
    encrypted = f.read()

decrypted = custom_decrypt(encrypted, key)
fields = parse_protobuf_wire_format(decrypted)
messages = extract_conversation_messages(fields)
```

### Message Filtering and Search

```python
def search_messages(results, keyword):
    """Search for keyword across all messages."""
    matches = []
    for result in results:
        if not result['success']:
            continue
        
        for i, msg in enumerate(result['messages']):
            if keyword.lower() in msg['content'].lower():
                matches.append({
                    'file': result['file'],
                    'message_number': i + 1,
                    'content': msg['content'],
                    'length': msg['length']
                })
    
    return matches

# Usage
results = [process_conversation_file(f, key) for f in files]
matches = search_messages(results, "important")
print(f"Found '{keyword}' in {len(matches)} messages")
```

### Export to Different Formats

```python
import json
import csv

def export_to_json(result, output_file):
    """Export to formatted JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def export_to_csv(result, output_file):
    """Export messages to CSV."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Message #', 'Content', 'Length'])
        
        for i, msg in enumerate(result['messages'], 1):
            writer.writerow([i, msg['content'], msg['length']])

def export_to_text(result, output_file):
    """Export to human-readable text."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"File: {result['file']}\n")
        f.write(f"Messages: {len(result['messages'])}\n")
        f.write("=" * 70 + "\n\n")
        
        for i, msg in enumerate(result['messages'], 1):
            f.write(f"--- Message {i} ({msg['length']} chars) ---\n")
            f.write(msg['content'])
            f.write("\n\n")

# Usage
result = process_conversation_file("chat.pb", key)
export_to_json(result, "output.json")
export_to_csv(result, "output.csv")
export_to_text(result, "output.txt")
```

### Integration with Data Analysis

```python
import pandas as pd
from collections import Counter

def analyze_conversations(results):
    """Analyze conversation patterns."""
    # Collect all messages
    all_messages = []
    for result in results:
        if result['success']:
            all_messages.extend(result['messages'])
    
    # Create DataFrame
    df = pd.DataFrame(all_messages)
    
    # Statistics
    stats = {
        'total_messages': len(df),
        'total_chars': df['length'].sum(),
        'avg_length': df['length'].mean(),
        'median_length': df['length'].median(),
        'min_length': df['length'].min(),
        'max_length': df['length'].max()
    }
    
    # Word frequency
    all_text = ' '.join(df['content'])
    words = all_text.split()
    word_freq = Counter(w.lower() for w in words if len(w) > 3)
    stats['top_words'] = word_freq.most_common(20)
    
    return stats

# Usage
results = [process_conversation_file(f, key) for f in files]
stats = analyze_conversations(results)
print(f"Average message length: {stats['avg_length']:.1f} characters")
```

---

## Best Practices

### 1. **Secure Key Management**

❌ **Don't:**
```python
key = base64.b64decode("qFl7rbZfqbZoahxeyCwdCg==")  # Hardcoded key
```

✅ **Do:**
```python
import os
key_b64 = os.environ.get('ANTIGRAVITY_KEY')
if not key_b64:
    key = get_key_from_keychain()
else:
    key = base64.b64decode(key_b64)
```

### 2. **Error Handling**

Always check the `success` flag:
```python
result = process_conversation_file(file_path, key)
if result['success']:
    # Process messages
    for msg in result['messages']:
        print(msg['content'])
else:
    # Handle error
    print(f"Failed: {result['error']}")
```

### 3. **Batch Processing with Progress**

Use progress feedback for long operations:
```python
from pathlib import Path

files = list(Path("conversations").glob("*.pb"))
for i, file in enumerate(files, 1):
    print_progress_bar(i, len(files), prefix='Processing:')
    result = process_conversation_file(str(file), key)
    # ... process result ...
```

### 4. **Memory Efficiency**

For large batches, process files one at a time:
```python
# ❌ Don't load all at once
results = [process_conversation_file(f, key) for f in files]

# ✅ Process incrementally
for file in files:
    result = process_conversation_file(file, key)
    process_and_save(result)  # Process immediately
    # Result goes out of scope
```

---

## See Also

- [README.md](README.md) - General documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [examples/](examples/) - Practical examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

**Need help?** Open an issue on [GitHub](https://github.com/arashz/antigravity_decryptor/issues)
