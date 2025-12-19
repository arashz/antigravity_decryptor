#!/bin/bash
# Basic Usage Examples for Antigravity Decryptor
# ===============================================

echo "🔓 Antigravity Decryptor - Basic Usage Examples"
echo ""

# Example 1: Decrypt a single file with key
echo "Example 1: Decrypt a single file"
echo "Command: python antigravity_decrypt.py conversation.pb --key \"YOUR_KEY\" --output conversation.json"
echo ""

# Example 2: Decrypt with environment variable
echo "Example 2: Use environment variable for key"
echo "Commands:"
echo "  export ANTIGRAVITY_KEY=\"YOUR_KEY\""
echo "  python antigravity_decrypt.py conversation.pb --output conversation.json"
echo ""

# Example 3: Decrypt to human-readable text
echo "Example 3: Get human-readable text output"
echo "Command: python antigravity_decrypt.py conversation.pb --format text --output conversation.txt"
echo ""

# Example 4: Batch process directory
echo "Example 4: Process all files in a directory"
echo "Command: python antigravity_decrypt.py ./conversations --output ./decrypted"
echo ""

# Example 5: Interactive mode
echo "Example 5: Use interactive mode (great for beginners!)"
echo "Command: python antigravity_decrypt.py --interactive"
echo ""

# Example 6: Verbose output for debugging
echo "Example 6: Verbose mode for troubleshooting"
echo "Command: python antigravity_decrypt.py conversation.pb --verbose"
echo ""

echo "💡 For more examples, see README.md or run: python antigravity_decrypt.py --help"
