# 🔐 Understanding the Antigravity File Format

A deep dive into how Antigravity IDE stores and encrypts conversation data.

## Table of Contents

- [File Format Overview](#file-format-overview)
- [Encryption Details](#encryption-details)
- [Protobuf Structure](#protobuf-structure)
- [Decryption Process](#decryption-process)
- [Common Variations](#common-variations)

---

## File Format Overview

### File Extension
```
.pb (Protocol Buffer)
```

### File Structure
```
┌─────────────────────────────────────────────────┐
│  Antigravity Conversation File (.pb)           │
├─────────────────────────────────────────────────┤
│  [Optional Header: 0-4 bytes]                   │
│  [IV/Nonce: 16 bytes]                          │
│  [Encrypted Protobuf Data: Variable length]    │
└─────────────────────────────────────────────────┘
```

### Size
- Typical range: **50 KB to 500 KB**
- Large conversations: **Up to several MB**

---

## Encryption Details

### Encryption Algorithm
**AES (Advanced Encryption Standard)**

The tool supports multiple AES modes:

```
┌──────────────────────────────────────────────┐
│  AES Encryption Modes Supported              │
├──────────────────────────────────────────────┤
│  1. AES-128-CTR (Counter Mode)              │
│     • Most common                            │
│     • Stream cipher mode                     │
│     • Uses 16-byte nonce/IV                 │
│                                             │
│  2. AES-128-CBC (Cipher Block Chaining)     │
│     • Block cipher mode                      │
│     • Requires padding                       │
│     • Uses 16-byte IV                       │
│                                             │
│  3. AES-128-GCM (Galois/Counter Mode)       │
│     • Authenticated encryption               │
│     • Built-in integrity check              │
│     • Uses 12-16 byte nonce                 │
└──────────────────────────────────────────────┘
```

### Key Details

**Key Size:** 16 bytes (128 bits)

**Key Format:** Base64 encoded string

```python
# Raw key (16 bytes)
raw_key = b'\xa0Y{\xad\xb6_\xa9\xb6hj\x1c~\x08,\x1d\n'

# Base64 encoded (for storage/transmission)
encoded_key = "qFl7rbZfqbZoahxeyCwdCg=="
```

**Key Storage Locations:**

1. **macOS Keychain** (recommended)
   - Service: `Antigravity Safe Storage`
   - Account: `Antigravity Key`
   - Automatically accessed by the tool

2. **Environment Variable**
   ```bash
   export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
   ```

3. **Command-line Argument**
   ```bash
   --key "qFl7rbZfqbZoahxeyCwdCg=="
   ```

---

## Protobuf Structure

### What is Protocol Buffer?

Protocol Buffer (protobuf) is a binary serialization format developed by Google.

**Key Features:**
- 🔹 Compact binary format
- 🔹 Language-neutral
- 🔹 Schema-based (but we parse without schema!)
- 🔹 Efficient for structured data

### Wire Format Basics

Protobuf uses a "wire format" for encoding data:

```
┌──────────────────────────────────────────────────┐
│  Protobuf Wire Format Structure                  │
├──────────────────────────────────────────────────┤
│  Each field consists of:                         │
│                                                  │
│  [Tag] [Value]                                   │
│                                                  │
│  Tag = (field_number << 3) | wire_type          │
└──────────────────────────────────────────────────┘
```

### Wire Types

```
┌─────────┬──────────────────┬────────────────────────┐
│ Type    │ Meaning          │ Used For               │
├─────────┼──────────────────┼────────────────────────┤
│ 0       │ Varint           │ int32, int64, bool     │
│ 1       │ Fixed64          │ double, fixed64        │
│ 2       │ Length-delimited │ string, bytes, message │
│ 5       │ Fixed32          │ float, fixed32         │
└─────────┴──────────────────┴────────────────────────┘
```

### Example Protobuf Structure

```
┌────────────────────────────────────────────────┐
│  Typical Antigravity Conversation Structure    │
├────────────────────────────────────────────────┤
│  Field 1 (type 2): Nested Message             │
│    ├─ Field 1 (type 2): String (user msg)    │
│    └─ Field 2 (type 2): String (AI response)  │
│                                                │
│  Field 2 (type 2): Nested Message             │
│    ├─ Field 1 (type 2): String (user msg)    │
│    └─ Field 2 (type 2): String (AI response)  │
│                                                │
│  Field 3 (type 0): Metadata (varint)          │
│                                                │
│  Field 4 (type 2): Additional nested data     │
└────────────────────────────────────────────────┘
```

---

## Decryption Process

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Read Encrypted File                           │
│  ───────────────────────────────────────────────────── │
│  • Read .pb file from disk                             │
│  • Entire file is encrypted                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Get Encryption Key                            │
│  ───────────────────────────────────────────────────── │
│  Priority order:                                        │
│  1. Command-line argument (--key)                      │
│  2. Environment variable (ANTIGRAVITY_KEY)             │
│  3. macOS Keychain (automatic)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Try Different Decryption Methods              │
│  ───────────────────────────────────────────────────── │
│  For each skip amount (0-4 bytes):                     │
│    For each encryption mode (CTR, CBC, GCM):           │
│      1. Skip header bytes (if any)                     │
│      2. Extract IV/nonce (first 16 bytes)              │
│      3. Attempt decryption                             │
│      4. If successful, proceed to Step 4               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 4: Parse Protobuf Wire Format                    │
│  ───────────────────────────────────────────────────── │
│  • Parse binary data without schema                     │
│  • Extract all fields recursively                      │
│  • Identify string fields (potential messages)         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 5: Extract Messages                              │
│  ───────────────────────────────────────────────────── │
│  • Recursively search for UTF-8 strings                │
│  • Filter out non-message data                         │
│  • Return structured message list                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 6: Output Results                                │
│  ───────────────────────────────────────────────────── │
│  • Format as JSON or text                              │
│  • Include metadata                                     │
│  • Save to file or stdout                              │
└─────────────────────────────────────────────────────────┘
```

### Detailed Decryption Algorithm

```python
# Pseudocode for decryption process

function decrypt_file(file_path, key):
    # Read file
    encrypted_data = read_file(file_path)
    
    # Try different configurations
    for skip_amount in [0, 1, 2, 3, 4]:
        for encryption_mode in [AES_CTR, AES_CBC, AES_GCM]:
            try:
                # Skip header bytes
                data = encrypted_data[skip_amount:]
                
                # Extract IV (first 16 bytes)
                iv = data[:16]
                ciphertext = data[16:]
                
                # Attempt decryption
                if encryption_mode == AES_CTR:
                    decrypted = decrypt_aes_ctr(ciphertext, key, iv)
                elif encryption_mode == AES_CBC:
                    decrypted = decrypt_aes_cbc(ciphertext, key, iv)
                elif encryption_mode == AES_GCM:
                    decrypted = decrypt_aes_gcm(ciphertext, key, iv)
                
                # Verify it's valid protobuf
                if is_valid_protobuf(decrypted):
                    return decrypted
                    
            except Exception:
                continue  # Try next configuration
    
    return None  # Decryption failed
```

---

## Common Variations

### Header Bytes

Some files have 0-4 header bytes before encryption:

```
┌──────────────────────────────────────────────────┐
│  Variation A: No Header (most common)            │
│  [IV: 16 bytes][Encrypted Data]                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Variation B: 1-byte Header                      │
│  [Header: 1][IV: 16 bytes][Encrypted Data]       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Variation C: 2-byte Header                      │
│  [Header: 2][IV: 16 bytes][Encrypted Data]       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Variation D: 4-byte Header                      │
│  [Header: 4][IV: 16 bytes][Encrypted Data]       │
└──────────────────────────────────────────────────┘
```

**Why it matters:** The tool automatically tries all skip amounts to handle these variations.

### Padding (CBC Mode)

CBC mode requires padding to align data to block size:

```
Original data: [XXXXXXXXX] (9 bytes)
After padding: [XXXXXXXXX0000000] (16 bytes)
                         ↑
                    PKCS#7 padding
```

### Protobuf Alignment

After decryption, data might need additional skipping:

```
Decrypted data: [??PROTOBUF_DATA...]
                 ↑
            May need to skip 0-4 bytes
            to align with protobuf start
```

---

## Data Flow Diagram

```
   User File (conversation.pb)
          ↓
   [Encrypted Binary Data]
          ↓
    ┌─────────┐
    │ AES Key │ ← From Keychain/Env/CLI
    └─────────┘
          ↓
   [Decrypted Binary Data]
          ↓
   ┌──────────────────┐
   │ Protobuf Parser  │
   └──────────────────┘
          ↓
   [Parsed Fields Structure]
   ├─ Field 1: Nested Message
   │  ├─ String: "Hello..."
   │  └─ String: "Response..."
   ├─ Field 2: Nested Message
   │  └─ ...
   └─ Field 3: Metadata
          ↓
   ┌──────────────────────┐
   │ Message Extractor    │
   └──────────────────────┘
          ↓
   [Extracted Messages]
   ├─ Message 1: "Hello..."
   ├─ Message 2: "Response..."
   └─ Message 3: "..."
          ↓
   ┌──────────────────┐
   │ Output Formatter │
   └──────────────────┘
          ↓
   JSON / Text Output
```

---

## Hex Dump Example

Here's what a real file looks like in hex:

```
$ hexdump -C conversation.pb | head -n 5

00000000  a8 59 c3 4f 2a 1b 8e f9  3c 2d 5a 78 b1 c4 23 6f  |.Y.O*...<-Zx..#o|
           ↑                                              ↑
           Start of IV/Nonce (16 bytes)                  

00000010  d2 8a 3b 4c 91 5e 6f 8d  a3 c7 1f 92 4b 5d 8e 3a  |..;L.^o.....K].:|
                                                           ↑
                                              End of IV, start of encrypted data

00000020  7f 2c 94 5b 63 d1 8f 4e  a9 1c 6d 85 3f 7a b2 58  |.,.[c..N..m.?z.X|
           ↑
           Encrypted protobuf data continues...
```

After decryption and parsing:

```
Field 1 (type 2, length-delimited):
  Nested Message:
    Field 1 (type 2): "How can I implement a binary search tree?"
    Field 2 (type 2): "Here's a comprehensive implementation..."
    
Field 2 (type 0, varint): 1234567890
Field 3 (type 2, length-delimited): [binary data]
```

---

## Technical Specifications

### File Characteristics

| Property | Value |
|----------|-------|
| **Extension** | `.pb` |
| **Format** | Encrypted Protocol Buffer |
| **Encryption** | AES-128 (CTR/CBC/GCM) |
| **Key Size** | 16 bytes (128 bits) |
| **IV/Nonce Size** | 16 bytes (typically) |
| **Typical Size** | 50 KB - 2 MB |

### Protobuf Specifications

| Property | Value |
|----------|-------|
| **Encoding** | Wire format (binary) |
| **Schema** | Not required (dynamic parsing) |
| **String Encoding** | UTF-8 |
| **Byte Order** | Little-endian |
| **Varint Encoding** | Base 128 |

---

## Troubleshooting Format Issues

### Issue: "Could not parse protobuf"

**Possible causes:**

1. **Wrong skip amount**
   ```bash
   # Tool tries all skip amounts automatically
   # If this fails, file may be corrupted
   ```

2. **Invalid decryption**
   ```python
   # Decryption succeeded but data is corrupted
   # Verify key is correct
   ```

3. **Not a protobuf file**
   ```bash
   # Check file type
   file conversation.pb
   
   # Check first bytes (should be binary, not text)
   head -c 100 conversation.pb | hexdump -C
   ```

### Issue: "Decryption failed"

**Diagnosis steps:**

```bash
# 1. Check file size (should not be 0 or too small)
ls -lh conversation.pb

# 2. Check it's a binary file
file conversation.pb

# 3. Verify key is base64 encoded
echo "qFl7rbZfqbZoahxeyCwdCg==" | base64 -d | wc -c
# Should output: 16

# 4. Try with verbose mode
python antigravity_decrypt.py conversation.pb --key "YOUR_KEY" --verbose
```

---

## Understanding Output Formats

### JSON Output

```json
{
  "file": "conversation.pb",
  "success": true,
  "messages": [
    {
      "content": "Full message text...",
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

### Text Output

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

---

## Advanced Topics

### Custom Parsing

If you need custom parsing logic:

```python
from antigravity_decrypt import decrypt_file, parse_protobuf_wire_format

# Decrypt
decrypted = decrypt_file("conversation.pb", key)

# Parse with custom depth
fields = parse_protobuf_wire_format(decrypted, max_depth=20)

# Custom extraction logic
def extract_specific_field(fields, field_number):
    """Extract a specific field number."""
    for field in fields:
        if field['field_number'] == field_number:
            return field
    return None

# Use it
specific_field = extract_specific_field(fields, 1)
```

### Binary Analysis

For deep inspection:

```python
def analyze_binary_structure(data):
    """Analyze binary structure of decrypted data."""
    print(f"Total size: {len(data)} bytes")
    print(f"First 16 bytes (hex): {data[:16].hex()}")
    
    # Check for protobuf markers
    has_varint = any(b & 0x80 for b in data[:100])
    print(f"Contains varints: {has_varint}")
    
    # Check UTF-8 content
    try:
        sample = data[:1000].decode('utf-8', errors='ignore')
        print(f"Sample text: {sample[:100]}")
    except:
        print("No readable text in first 1000 bytes")

# Usage
decrypted = decrypt_file("conversation.pb", key)
analyze_binary_structure(decrypted)
```

---

## See Also

- 📖 [API Reference](API_REFERENCE.md) - Complete API documentation
- 🔍 [Analyzing Conversations](ANALYZING_CONVERSATIONS.md) - Analysis guide
- 🚀 [Quick Start](QUICKSTART.md) - Get started quickly
- 🐛 [Troubleshooting](TROUBLESHOOTING.md) - Common issues

---

**Need more technical details?** Open an issue on [GitHub](https://github.com/arashz/antigravity_decryptor/issues)
