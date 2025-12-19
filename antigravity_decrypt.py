#!/usr/bin/env python3
"""
Portable Antigravity IDE Conversation Decryptor
================================================

Decrypts and extracts human-readable conversations from Antigravity IDE's
encrypted .pb conversation files.

Usage:
    python antigravity_decrypt.py <input.pb> [--output <output.json>] [--key <key>]
    python antigravity_decrypt.py <directory> [--output <output_dir>] [--key <key>]

Requirements:
    pip install cryptography protobuf

Author: Arash Zolfaghari
"""

import sys
import os
import json
import base64
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import struct

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
except ImportError:
    print("Error: cryptography library required. Install with: pip install cryptography")
    sys.exit(1)

try:
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: protobuf library required. Install with: pip install protobuf")
    sys.exit(1)


# ============================================================================
# Encryption Key Management
# ============================================================================

def get_key_from_keychain() -> Optional[bytes]:
    """Retrieve encryption key from macOS Keychain."""
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'Antigravity Safe Storage',
             '-a', 'Antigravity Key', '-w'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        key_b64 = result.stdout.strip()
        return base64.b64decode(key_b64)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_key_from_env() -> Optional[bytes]:
    """Get key from ANTIGRAVITY_KEY environment variable."""
    key_b64 = os.environ.get('ANTIGRAVITY_KEY')
    if key_b64:
        try:
            return base64.b64decode(key_b64)
        except:
            pass
    return None


# ============================================================================
# Protobuf Wire Format Parser
# ============================================================================

def decode_varint(data: bytes, pos: int) -> Tuple[int, int]:
    """Decode a varint from the data starting at pos. Returns (value, new_pos)."""
    result = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")
    return result, pos


def decode_wire_field(data: bytes, pos: int, wire_type: int) -> Tuple[Any, int]:
    """Decode a single wire field. Returns (value, new_pos)."""
    if wire_type == 0:  # Varint
        return decode_varint(data, pos)
    elif wire_type == 1:  # Fixed64
        if pos + 8 > len(data):
            raise ValueError("Not enough data for fixed64")
        value = struct.unpack('<Q', data[pos:pos+8])[0]
        return value, pos + 8
    elif wire_type == 2:  # Length-delimited
        length, pos = decode_varint(data, pos)
        if pos + length > len(data):
            raise ValueError("Not enough data for length-delimited field")
        value = data[pos:pos+length]
        return value, pos + length
    elif wire_type == 5:  # Fixed32
        if pos + 4 > len(data):
            raise ValueError("Not enough data for fixed32")
        value = struct.unpack('<I', data[pos:pos+4])[0]
        return value, pos + 4
    else:
        raise ValueError(f"Unknown wire type: {wire_type}")


def parse_protobuf_wire_format(data: bytes, max_depth: int = 10, depth: int = 0) -> List[Dict[str, Any]]:
    """Parse protobuf wire format and extract field information."""
    if depth > max_depth:
        return []
    
    fields = []
    pos = 0
    max_iterations = 100000
    iteration = 0
    
    while pos < len(data) and iteration < max_iterations:
        iteration += 1
        try:
            tag, new_pos = decode_varint(data, pos)
            if new_pos == pos:
                break
            pos = new_pos
            field_number = tag >> 3
            wire_type = tag & 0x7
            
            value, new_pos = decode_wire_field(data, pos, wire_type)
            pos = new_pos
            
            interpreted_value = value
            if wire_type == 2:  # Length-delimited
                try:
                    if len(value) > 0 and len(value) < len(data):
                        nested_fields = parse_protobuf_wire_format(value, max_depth, depth + 1)
                        if nested_fields:
                            interpreted_value = {
                                "nested_fields": nested_fields,
                                "length": len(value)
                            }
                        else:
                            # Try as string
                            try:
                                decoded_str = value.decode('utf-8', errors='ignore')
                                if len(decoded_str) > 0:
                                    interpreted_value = {
                                        "as_string": decoded_str,
                                        "length": len(value)
                                    }
                            except:
                                interpreted_value = {"length": len(value)}
                except:
                    try:
                        decoded_str = value.decode('utf-8', errors='ignore')
                        interpreted_value = {
                            "as_string": decoded_str,
                            "length": len(value)
                        }
                    except:
                        interpreted_value = {"length": len(value)}
            
            fields.append({
                "field_number": field_number,
                "wire_type": wire_type,
                "wire_type_name": ["varint", "fixed64", "length-delimited", "start_group", "end_group", "fixed32"][wire_type] if wire_type < 6 else "unknown",
                "value": interpreted_value
            })
        except Exception as e:
            if fields:
                break
            return []
    
    return fields


# ============================================================================
# Decryption Functions
# ============================================================================

def decrypt_aes_ctr(data: bytes, key: bytes, skip_bytes: int = 0) -> Optional[bytes]:
    """Decrypt using AES-CTR mode."""
    try:
        data = data[skip_bytes:]
        if len(data) < 16:
            return None
        nonce = data[:16]
        encrypted_data = data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
    except:
        return None


def decrypt_aes_cbc(data: bytes, key: bytes, skip_bytes: int = 0) -> Optional[bytes]:
    """Decrypt using AES-CBC mode (fallback)."""
    try:
        data = data[skip_bytes:]
        if len(data) < 16:
            return None
        iv = data[:16]
        encrypted_data = data[16:]
        
        if len(encrypted_data) == 0 or len(encrypted_data) % 16 != 0:
            return None
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Try to remove PKCS7 padding
        try:
            unpadder = padding.PKCS7(128).unpadder()
            return unpadder.update(decrypted) + unpadder.finalize()
        except:
            return decrypted
    except:
        return None


def decrypt_aes_gcm(data: bytes, key: bytes, skip_bytes: int = 0) -> Optional[bytes]:
    """Decrypt using AES-GCM mode (fallback)."""
    try:
        data = data[skip_bytes:]
        if len(data) < 12:
            return None
        nonce = data[:12]
        encrypted_data = data[12:]
        
        if len(encrypted_data) < 16:
            return None
        
        ciphertext = encrypted_data[:-16]
        tag = encrypted_data[-16:]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    except:
        return None


def is_valid_protobuf(data: bytes, min_fields: int = 1) -> bool:
    """Check if data looks like valid protobuf."""
    try:
        fields = parse_protobuf_wire_format(data[:min(5000, len(data))])
        if not fields:
            return False
        valid_fields = [f for f in fields if isinstance(f, dict) and 'field_number' in f and 'error' not in f]
        return len(valid_fields) >= min_fields
    except:
        return False


def decrypt_file(file_path: str, key: bytes, verbose: bool = False) -> Optional[bytes]:
    """
    Decrypt an encrypted .pb file.
    Tries multiple encryption methods and skip amounts for resilience.
    """
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # List of decryption methods to try (in order of likelihood)
    decrypt_methods = [
        ("AES-CTR", decrypt_aes_ctr),
        ("AES-CBC", decrypt_aes_cbc),
        ("AES-GCM", decrypt_aes_gcm),
    ]
    
    # Try different encryption methods
    for method_name, decrypt_func in decrypt_methods:
        if verbose:
            print(f"  Trying {method_name}...", file=sys.stderr)
        
        # Try different skip amounts (some files have header bytes)
        for skip in [0, 1, 2, 4, 8]:  # Extended range for future compatibility
            decrypted = decrypt_func(encrypted_data, key, skip)
            if decrypted:
                # Try to validate as protobuf
                # Also try skipping a few bytes after decryption (some files need this)
                for post_skip in [0, 1, 2, 4, 8]:  # Extended range
                    test_data = decrypted[post_skip:]
                    if is_valid_protobuf(test_data):
                        if verbose:
                            print(f"  ✓ Success with {method_name} (skip {skip}, post-skip {post_skip})", file=sys.stderr)
                        return test_data
                    
                    # Also check if it has readable text (might be valid even if protobuf parsing fails)
                    try:
                        text_preview = test_data[:200].decode('utf-8', errors='ignore')
                        if len(text_preview) > 50 and text_preview.isprintable():
                            # Might be valid, return it
                            if verbose:
                                print(f"  ? {method_name} produced readable text (may be valid)", file=sys.stderr)
                            return test_data
                    except:
                        pass
    
    return None


# ============================================================================
# Text Extraction
# ============================================================================

def extract_text_from_fields(fields: List[Dict], max_length: int = 10000) -> List[str]:
    """Extract all readable text strings from protobuf fields."""
    texts = []
    
    def extract_recursive(field_list, depth=0):
        if depth > 10:
            return
        for field in field_list:
            if isinstance(field, dict):
                value = field.get('value', '')
                if isinstance(value, dict):
                    if 'as_string' in value:
                        text = value['as_string']
                        if text and len(text.strip()) > 5:
                            texts.append(text[:max_length])
                    if 'nested_fields' in value:
                        extract_recursive(value['nested_fields'], depth + 1)
                elif isinstance(value, (str, bytes)):
                    try:
                        if isinstance(value, bytes):
                            text = value.decode('utf-8', errors='ignore')
                        else:
                            text = value
                        if text and len(text.strip()) > 5:
                            texts.append(text[:max_length])
                    except:
                        pass
    
    extract_recursive(fields)
    return texts


def extract_conversation_messages(fields: List[Dict]) -> List[Dict[str, Any]]:
    """Extract conversation messages from protobuf structure."""
    messages = []
    texts = extract_text_from_fields(fields)
    
    # Filter and organize texts that look like messages
    for text in texts:
        # Skip very short or non-conversational text
        if len(text.strip()) < 10:
            continue
        
        # Skip binary-looking data
        if not any(c.isprintable() or c.isspace() for c in text[:100]):
            continue
        
        messages.append({
            "content": text.strip(),
            "length": len(text)
        })
    
    return messages


# ============================================================================
# Main Processing
# ============================================================================

def process_conversation_file(file_path: str, key: bytes, verbose: bool = False) -> Dict[str, Any]:
    """Process a single conversation file and extract readable content."""
    result = {
        "file": os.path.basename(file_path),
        "path": file_path,
        "success": False,
        "error": None,
        "messages": [],
        "metadata": {}
    }
    
    try:
        # Get file info
        stat = os.stat(file_path)
        result["metadata"] = {
            "size": stat.st_size,
            "modified": stat.st_mtime
        }
        
        # Decrypt
        decrypted = decrypt_file(file_path, key, verbose)
        if not decrypted:
            result["error"] = "Decryption failed"
            return result
        
        result["metadata"]["decrypted_size"] = len(decrypted)
        
        # Parse protobuf
        fields = parse_protobuf_wire_format(decrypted)
        if not fields:
            result["error"] = "Could not parse protobuf"
            return result
        
        # Extract messages
        messages = extract_conversation_messages(fields)
        result["messages"] = messages
        result["success"] = True
        result["metadata"]["field_count"] = len(fields)
        result["metadata"]["message_count"] = len(messages)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def format_conversation_output(result: Dict[str, Any], format_type: str = "json") -> str:
    """Format conversation result for output."""
    if format_type == "json":
        return json.dumps(result, indent=2, default=str)
    elif format_type == "text":
        output = []
        output.append(f"File: {result['file']}")
        output.append(f"Status: {'Success' if result['success'] else 'Failed'}")
        if result.get('error'):
            output.append(f"Error: {result['error']}")
        output.append(f"Messages: {result['metadata'].get('message_count', 0)}")
        output.append("")
        output.append("=" * 70)
        output.append("CONVERSATION CONTENT")
        output.append("=" * 70)
        output.append("")
        
        for i, msg in enumerate(result['messages'], 1):
            output.append(f"--- Message {i} ({msg['length']} chars) ---")
            output.append(msg['content'])
            output.append("")
        
        return "\n".join(output)
    else:
        return str(result)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Decrypt and extract Antigravity IDE conversation files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decrypt a single file
  python antigravity_decrypt.py conversation.pb --output conversation.json
  
  # Decrypt all files in a directory
  python antigravity_decrypt.py ./conversations --output ./decrypted
  
  # Use custom key (base64 encoded)
  python antigravity_decrypt.py conversation.pb --key "qFl7rbZfqbZoahxeyCwdCg=="
  
  # Set key via environment variable
  export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
  python antigravity_decrypt.py conversation.pb
        """
    )
    
    parser.add_argument('input', help='Input .pb file or directory containing .pb files')
    parser.add_argument('--output', '-o', help='Output file or directory (default: stdout or input_decrypted/)')
    parser.add_argument('--key', '-k', help='Encryption key (base64 encoded). If not provided, tries keychain or ANTIGRAVITY_KEY env var')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format (default: json)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Get encryption key
    key = None
    if args.key:
        try:
            key = base64.b64decode(args.key)
        except:
            print(f"Error: Invalid key format. Key must be base64 encoded.", file=sys.stderr)
            sys.exit(1)
    else:
        key = get_key_from_keychain()
        if not key:
            key = get_key_from_env()
    
    if not key:
        print("Error: Could not retrieve encryption key.", file=sys.stderr)
        print("  Options:", file=sys.stderr)
        print("  1. Use --key option with base64 encoded key", file=sys.stderr)
        print("  2. Set ANTIGRAVITY_KEY environment variable", file=sys.stderr)
        print("  3. On macOS, key will be retrieved from Keychain", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Using encryption key: {key.hex()[:32]}...", file=sys.stderr)
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        if args.verbose:
            print(f"Processing file: {input_path}", file=sys.stderr)
        
            result = process_conversation_file(str(input_path), key, args.verbose)
        output = format_conversation_output(result, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if args.verbose:
                print(f"Output written to: {args.output}", file=sys.stderr)
        else:
            print(output)
    
    elif input_path.is_dir():
        # Directory of files
        pb_files = list(input_path.glob("*.pb"))
        if not pb_files:
            print(f"Error: No .pb files found in {input_path}", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"Found {len(pb_files)} .pb files", file=sys.stderr)
        
        output_dir = Path(args.output) if args.output else input_path / "decrypted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, pb_file in enumerate(pb_files, 1):
            if args.verbose:
                print(f"[{i}/{len(pb_files)}] Processing {pb_file.name}...", file=sys.stderr)
            
            result = process_conversation_file(str(pb_file), key, args.verbose)
            results.append(result)
            
            # Save individual file
            output_file = output_dir / f"{pb_file.stem}_decrypted.{args.format}"
            output = format_conversation_output(result, args.format)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        
        # Save summary
        summary_file = output_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_files": len(pb_files),
                "successful": sum(1 for r in results if r['success']),
                "failed": sum(1 for r in results if not r['success']),
                "total_messages": sum(len(r['messages']) for r in results),
                "files": results
            }, f, indent=2, default=str)
        
        if args.verbose:
            print(f"\nSummary:", file=sys.stderr)
            print(f"  Total files: {len(pb_files)}", file=sys.stderr)
            print(f"  Successful: {sum(1 for r in results if r['success'])}", file=sys.stderr)
            print(f"  Failed: {sum(1 for r in results if not r['success'])}", file=sys.stderr)
            print(f"  Total messages: {sum(len(r['messages']) for r in results)}", file=sys.stderr)
            print(f"  Output directory: {output_dir}", file=sys.stderr)
    
    else:
        print(f"Error: {input_path} is not a file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

