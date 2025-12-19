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

__version__ = "1.1.0"

import sys
import os
import json
import base64
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import struct
import time

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
# UI/UX Utilities
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    
    @staticmethod
    def is_supported():
        """Check if terminal supports colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    @classmethod
    def disable(cls):
        """Disable colors for non-TTY environments."""
        cls.RESET = cls.BOLD = cls.DIM = ''
        cls.RED = cls.GREEN = cls.YELLOW = ''
        cls.BLUE = cls.MAGENTA = cls.CYAN = ''


# Auto-detect color support
if not Colors.is_supported():
    Colors.disable()


def print_success(message: str):
    """Print success message with color."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_error(message: str):
    """Print error message with color."""
    print(f"{Colors.RED}✗{Colors.RESET} {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message with color."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}", file=sys.stderr)


def print_info(message: str):
    """Print info message with color."""
    print(f"{Colors.CYAN}ℹ{Colors.RESET} {message}", file=sys.stderr)


def print_header(message: str):
    """Print header with styling."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")


def print_progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', length: int = 40):
    """Print a progress bar."""
    if total == 0:
        return
    
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    
    print(f'\r{prefix} |{Colors.CYAN}{bar}{Colors.RESET}| {current}/{total} {suffix}', end='', flush=True)
    
    if current == total:
        print()  # New line on completion


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
# Interactive Mode
# ============================================================================

def interactive_mode(args):
    """Interactive mode for beginners."""
    print_header("🔓 Antigravity Decryptor - Interactive Mode")
    print(f"\n{Colors.BOLD}Welcome!{Colors.RESET} This tool decrypts Antigravity IDE conversation files.\n")
    
    # Get input path
    if not args.input:
        print(f"{Colors.CYAN}Step 1:{Colors.RESET} Input file or directory")
        input_path = input(f"  Enter path to .pb file or directory: ").strip()
        if not input_path:
            print_error("No input provided. Exiting.")
            sys.exit(1)
        args.input = input_path
    
    # Get key if not provided
    if not args.key:
        print(f"\n{Colors.CYAN}Step 2:{Colors.RESET} Encryption key")
        print(f"  You can:")
        print(f"    1. Enter key now (base64 encoded)")
        print(f"    2. Press Enter to try environment variable or Keychain")
        key_input = input(f"  Enter key (or press Enter to auto-detect): ").strip()
        if key_input:
            args.key = key_input
    
    # Get output path
    if not args.output:
        print(f"\n{Colors.CYAN}Step 3:{Colors.RESET} Output location")
        input_obj = Path(args.input)
        if input_obj.is_file():
            default_output = str(input_obj.with_suffix('.json'))
        else:
            default_output = str(input_obj / "decrypted")
        
        print(f"  Default: {Colors.DIM}{default_output}{Colors.RESET}")
        output_input = input(f"  Enter output path (or press Enter for default): ").strip()
        args.output = output_input if output_input else default_output
    
    # Get format
    if not args.format or args.format == 'json':
        print(f"\n{Colors.CYAN}Step 4:{Colors.RESET} Output format")
        print(f"  1. JSON (default) - Structured data")
        print(f"  2. Text - Human-readable")
        format_choice = input(f"  Choose format (1/2 or press Enter for JSON): ").strip()
        if format_choice == '2':
            args.format = 'text'
    
    print_header("\n🚀 Starting decryption...")
    print(f"  Input: {Colors.CYAN}{args.input}{Colors.RESET}")
    print(f"  Output: {Colors.CYAN}{args.output}{Colors.RESET}")
    print(f"  Format: {Colors.CYAN}{args.format}{Colors.RESET}\n")
    
    # Continue with regular processing
    return process_with_args(args)


# ============================================================================
# CLI Interface
# ============================================================================

def process_with_args(args):
    """Process files with parsed arguments."""
    # Get encryption key
    key = None
    if args.key:
        try:
            key = base64.b64decode(args.key)
        except:
            print_error("Invalid key format. Key must be base64 encoded.")
            print_info("Example: qFl7rbZfqbZoahxeyCwdCg==")
            sys.exit(1)
    else:
        key = get_key_from_keychain()
        if not key:
            key = get_key_from_env()
    
    if not key:
        print_error("Could not retrieve encryption key.")
        print_info("You have several options to provide the encryption key:")
        print(f"  {Colors.BOLD}1.{Colors.RESET} Use --key option: {Colors.DIM}python antigravity_decrypt.py file.pb --key \"YOUR_KEY\"{Colors.RESET}", file=sys.stderr)
        print(f"  {Colors.BOLD}2.{Colors.RESET} Set environment variable: {Colors.DIM}export ANTIGRAVITY_KEY=\"YOUR_KEY\"{Colors.RESET}", file=sys.stderr)
        print(f"  {Colors.BOLD}3.{Colors.RESET} On macOS: Key is auto-retrieved from Keychain (service: 'Antigravity Safe Storage')", file=sys.stderr)
        print(f"\n{Colors.YELLOW}💡 Tip:{Colors.RESET} The key should be base64 encoded (e.g., 'qFl7rbZfqbZoahxeyCwdCg==')", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print_info(f"Using encryption key: {key.hex()[:32]}...")
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file
        if args.verbose:
            print_header(f"📄 Processing file: {input_path.name}")
        
        result = process_conversation_file(str(input_path), key, args.verbose)
        output = format_conversation_output(result, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if result['success']:
                print_success(f"Successfully decrypted and saved to: {args.output}")
                if result['metadata'].get('message_count', 0) > 0:
                    print_info(f"Extracted {result['metadata']['message_count']} messages")
            else:
                print_error(f"Failed to decrypt: {result.get('error', 'Unknown error')}")
        else:
            print(output)
    
    elif input_path.is_dir():
        # Directory of files
        pb_files = list(input_path.glob("*.pb"))
        if not pb_files:
            print_error(f"No .pb files found in {input_path}")
            print_info(f"Looking for files with .pb extension in: {input_path.absolute()}")
            sys.exit(1)
        
        print_header(f"📁 Batch Processing: {len(pb_files)} files found")
        
        output_dir = Path(args.output) if args.output else input_path / "decrypted"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        successful = 0
        failed = 0
        
        for i, pb_file in enumerate(pb_files, 1):
            # Show progress bar
            if not args.verbose:
                print_progress_bar(i - 1, len(pb_files), prefix='Progress:', suffix=f'{pb_file.name[:30]}...')
            else:
                print_info(f"[{i}/{len(pb_files)}] Processing {pb_file.name}...")
            
            result = process_conversation_file(str(pb_file), key, args.verbose)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
            
            # Save individual file
            output_file = output_dir / f"{pb_file.stem}_decrypted.{args.format}"
            output = format_conversation_output(result, args.format)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        
        # Complete progress bar
        if not args.verbose:
            print_progress_bar(len(pb_files), len(pb_files), prefix='Progress:', suffix='Complete!')
        
        # Save summary
        summary_file = output_dir / "summary.json"
        total_messages = sum(len(r['messages']) for r in results)
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_files": len(pb_files),
                "successful": successful,
                "failed": failed,
                "total_messages": total_messages,
                "files": results
            }, f, indent=2, default=str)
        
        # Print summary
        print_header("\n📊 Summary")
        print(f"  {Colors.GREEN}✓{Colors.RESET} Successful: {Colors.BOLD}{successful}{Colors.RESET}/{len(pb_files)}")
        if failed > 0:
            print(f"  {Colors.RED}✗{Colors.RESET} Failed: {Colors.BOLD}{failed}{Colors.RESET}/{len(pb_files)}")
        print(f"  💬 Total messages extracted: {Colors.BOLD}{total_messages}{Colors.RESET}")
        print(f"  📂 Output directory: {Colors.CYAN}{output_dir}{Colors.RESET}")
        print(f"  📄 Summary saved to: {Colors.CYAN}{summary_file}{Colors.RESET}")
        
        if failed > 0:
            print_warning(f"\n{failed} file(s) failed. Check summary.json for details.")
    
    else:
        print_error(f"{input_path} is not a file or directory")
        print_info(f"Please provide a valid .pb file or directory containing .pb files")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}🔓 Antigravity IDE Conversation Decryptor{Colors.RESET} v{__version__}\n\nDecrypt and extract human-readable conversations from Antigravity IDE's encrypted .pb files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}Examples:{Colors.RESET}
  {Colors.CYAN}# Decrypt a single file{Colors.RESET}
  python antigravity_decrypt.py conversation.pb --output conversation.json
  
  {Colors.CYAN}# Decrypt all files in a directory with progress tracking{Colors.RESET}
  python antigravity_decrypt.py ./conversations --output ./decrypted
  
  {Colors.CYAN}# Use custom key (base64 encoded){Colors.RESET}
  python antigravity_decrypt.py conversation.pb --key "qFl7rbZfqbZoahxeyCwdCg=="
  
  {Colors.CYAN}# Set key via environment variable{Colors.RESET}
  export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
  python antigravity_decrypt.py conversation.pb
  
  {Colors.CYAN}# Get human-readable text output{Colors.RESET}
  python antigravity_decrypt.py conversation.pb --format text --output conversation.txt
  
  {Colors.CYAN}# Interactive mode for beginners{Colors.RESET}
  python antigravity_decrypt.py --interactive

{Colors.BOLD}Key Management:{Colors.RESET}
  Priority order: --key argument → ANTIGRAVITY_KEY env var → macOS Keychain
  
{Colors.BOLD}Need Help?{Colors.RESET}
  See README.md or visit: https://github.com/arashz/antigravity_decryptor
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input .pb file or directory containing .pb files')
    parser.add_argument('--output', '-o', help='Output file or directory (default: stdout for files, ./decrypted for directories)')
    parser.add_argument('--key', '-k', help='Encryption key (base64 encoded). Alternative: use ANTIGRAVITY_KEY env var')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format (default: json)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed processing information')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode with prompts')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or not args.input:
        return interactive_mode(args)
    
    return process_with_args(args)


if __name__ == '__main__':
    main()

