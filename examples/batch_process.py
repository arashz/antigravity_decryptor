#!/usr/bin/env python3
"""
Example: Batch Processing with Python API
==========================================

This example shows how to use the Antigravity Decryptor programmatically
to batch process multiple conversation files.

⚠️ SECURITY NOTE: This example contains placeholder keys marked as 
"YOUR_KEY_HERE_REPLACE_ME". Always replace these with your actual key
or use environment variables in production. Never commit real keys to 
version control!
"""

import sys
import base64
from pathlib import Path

# Import decryptor functions
# Note: In a real scenario, you would either:
# 1. Install the package: pip install antigravity-decryptor
# 2. Or add the script to your Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from antigravity_decrypt import (
    decrypt_file,
    parse_protobuf_wire_format,
    extract_conversation_messages,
    process_conversation_file
)


def batch_process_example():
    """Example of batch processing conversation files."""
    
    # Your encryption key (base64 encoded)
    # ⚠️ WARNING: Replace with your actual key! This is just a placeholder example.
    # Get your key from environment variable or Keychain in production.
    key_b64 = "YOUR_KEY_HERE_REPLACE_ME"  # ← Replace this!
    
    # In production, use environment variable:
    # key_b64 = os.environ.get('ANTIGRAVITY_KEY')
    
    key = base64.b64decode(key_b64)
    
    # Directory containing .pb files
    conversations_dir = Path("./conversations")
    output_dir = Path("./decrypted_output")
    output_dir.mkdir(exist_ok=True)
    
    # Find all .pb files
    pb_files = list(conversations_dir.glob("*.pb"))
    
    if not pb_files:
        print(f"No .pb files found in {conversations_dir}")
        return
    
    print(f"Found {len(pb_files)} conversation files")
    print("-" * 50)
    
    results = []
    for i, pb_file in enumerate(pb_files, 1):
        print(f"[{i}/{len(pb_files)}] Processing: {pb_file.name}")
        
        # Process the file
        result = process_conversation_file(str(pb_file), key, verbose=False)
        results.append(result)
        
        # Print summary
        if result['success']:
            msg_count = result['metadata'].get('message_count', 0)
            print(f"  ✓ Success: {msg_count} messages extracted")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total_messages = sum(len(r['messages']) for r in results if r['success'])
    
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total files: {len(pb_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(pb_files) - successful}")
    print(f"Total messages: {total_messages}")


def single_file_example():
    """Example of processing a single file with custom logic."""
    
    # Your encryption key (base64 encoded)
    # ⚠️ WARNING: Replace with your actual key! This is just a placeholder example.
    key_b64 = "YOUR_KEY_HERE_REPLACE_ME"  # ← Replace this!
    
    # In production, use environment variable:
    # key_b64 = os.environ.get('ANTIGRAVITY_KEY')
    
    key = base64.b64decode(key_b64)
    
    # File to decrypt
    file_path = "./conversation.pb"
    
    print(f"Decrypting: {file_path}")
    
    # Step 1: Decrypt the file
    decrypted = decrypt_file(file_path, key)
    if not decrypted:
        print("✗ Decryption failed!")
        return
    
    print(f"✓ Decryption successful ({len(decrypted)} bytes)")
    
    # Step 2: Parse protobuf structure
    fields = parse_protobuf_wire_format(decrypted)
    print(f"✓ Parsed {len(fields)} protobuf fields")
    
    # Step 3: Extract messages
    messages = extract_conversation_messages(fields)
    print(f"✓ Extracted {len(messages)} messages")
    
    # Step 4: Process messages
    print("\n" + "=" * 50)
    print("MESSAGES")
    print("=" * 50)
    
    for i, msg in enumerate(messages, 1):
        print(f"\nMessage {i} ({msg['length']} chars):")
        print("-" * 50)
        # Print first 200 characters
        preview = msg['content'][:200]
        print(preview)
        if len(msg['content']) > 200:
            print("...")


if __name__ == "__main__":
    print("🔓 Antigravity Decryptor - Python API Examples\n")
    
    # Choose which example to run
    print("Choose an example:")
    print("  1. Batch process directory")
    print("  2. Single file with custom logic")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        batch_process_example()
    elif choice == "2":
        single_file_example()
    else:
        print("Invalid choice!")
