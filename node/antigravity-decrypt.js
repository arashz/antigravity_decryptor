#!/usr/bin/env node

/**
 * Portable Antigravity IDE Conversation Decryptor
 * ================================================
 * 
 * Decrypts and extracts human-readable conversations from Antigravity IDE's
 * encrypted .pb conversation files.
 * 
 * Usage:
 *     node antigravity-decrypt.js <input.pb> [--output <output.json>] [--key <key>]
 *     node antigravity-decrypt.js <directory> [--output <output_dir>] [--key <key>]
 * 
 * Requirements:
 *     Node.js 14.0.0 or higher (no external dependencies required)
 * 
 * Author: Arash Zolfaghari
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const VERSION = '1.1.0';

// ============================================================================
// UI/UX Utilities
// ============================================================================

class Colors {
  static RESET = '\x1b[0m';
  static BOLD = '\x1b[1m';
  static DIM = '\x1b[2m';
  static RED = '\x1b[91m';
  static GREEN = '\x1b[92m';
  static YELLOW = '\x1b[93m';
  static BLUE = '\x1b[94m';
  static MAGENTA = '\x1b[95m';
  static CYAN = '\x1b[96m';

  static isSupported() {
    return process.stdout.isTTY;
  }

  static disable() {
    this.RESET = this.BOLD = this.DIM = '';
    this.RED = this.GREEN = this.YELLOW = '';
    this.BLUE = this.MAGENTA = this.CYAN = '';
  }
}

// Auto-detect color support
if (!Colors.isSupported()) {
  Colors.disable();
}

function printSuccess(message) {
  console.log(`${Colors.GREEN}✓${Colors.RESET} ${message}`);
}

function printError(message) {
  console.error(`${Colors.RED}✗${Colors.RESET} ${message}`);
}

function printWarning(message) {
  console.error(`${Colors.YELLOW}⚠${Colors.RESET} ${message}`);
}

function printInfo(message) {
  console.error(`${Colors.CYAN}ℹ${Colors.RESET} ${message}`);
}

function printHeader(message) {
  console.log(`\n${Colors.BOLD}${Colors.CYAN}${message}${Colors.RESET}`);
}

function printProgressBar(current, total, prefix = '', suffix = '', length = 40) {
  if (total === 0) return;
  
  const percent = current / total;
  const filled = Math.floor(length * percent);
  const bar = '█'.repeat(filled) + '░'.repeat(length - filled);
  
  process.stderr.write(`\r${prefix} |${Colors.CYAN}${bar}${Colors.RESET}| ${current}/${total} ${suffix}`);
  
  if (current === total) {
    process.stderr.write('\n');
  }
}

// ============================================================================
// Encryption Key Management
// ============================================================================

function getKeyFromKeychain() {
  try {
    if (process.platform !== 'darwin') {
      return null;
    }
    const result = execSync(
      'security find-generic-password -s "Antigravity Safe Storage" -a "Antigravity Key" -w',
      { encoding: 'utf8', timeout: 5000, stdio: ['pipe', 'pipe', 'ignore'] }
    );
    const keyB64 = result.trim();
    return Buffer.from(keyB64, 'base64');
  } catch {
    return null;
  }
}

function getKeyFromEnv() {
  const keyB64 = process.env.ANTIGRAVITY_KEY;
  if (keyB64) {
    try {
      return Buffer.from(keyB64, 'base64');
    } catch {
      return null;
    }
  }
  return null;
}

// ============================================================================
// Protobuf Wire Format Parser
// ============================================================================

function decodeVarint(data, pos) {
  let result = 0;
  let shift = 0;
  while (pos < data.length) {
    const byte = data[pos];
    pos++;
    result |= (byte & 0x7F) << shift;
    if (!(byte & 0x80)) {
      break;
    }
    shift += 7;
    if (shift >= 64) {
      throw new Error('Varint too long');
    }
  }
  return { value: result, pos };
}

function decodeWireField(data, pos, wireType) {
  if (wireType === 0) { // Varint
    return decodeVarint(data, pos);
  } else if (wireType === 1) { // Fixed64
    if (pos + 8 > data.length) {
      throw new Error('Not enough data for fixed64');
    }
    const value = data.readBigUInt64LE(pos);
    return { value: Number(value), pos: pos + 8 };
  } else if (wireType === 2) { // Length-delimited
    const { value: length, pos: newPos } = decodeVarint(data, pos);
    if (newPos + length > data.length) {
      throw new Error('Not enough data for length-delimited field');
    }
    const value = data.slice(newPos, newPos + length);
    return { value, pos: newPos + length };
  } else if (wireType === 5) { // Fixed32
    if (pos + 4 > data.length) {
      throw new Error('Not enough data for fixed32');
    }
    const value = data.readUInt32LE(pos);
    return { value, pos: pos + 4 };
  } else {
    throw new Error(`Unknown wire type: ${wireType}`);
  }
}

function parseProtobufWireFormat(data, maxDepth = 10, depth = 0) {
  if (depth > maxDepth) {
    return [];
  }

  const fields = [];
  let pos = 0;
  const maxIterations = 100000;
  let iteration = 0;

  while (pos < data.length && iteration < maxIterations) {
    iteration++;
    try {
      const { value: tag, pos: newPos } = decodeVarint(data, pos);
      if (newPos === pos) break;
      pos = newPos;

      const fieldNumber = tag >> 3;
      const wireType = tag & 0x7;

      const { value, pos: finalPos } = decodeWireField(data, pos, wireType);
      pos = finalPos;

      let interpretedValue = value;
      if (wireType === 2) { // Length-delimited
        try {
          if (value.length > 0 && value.length < data.length) {
            const nestedFields = parseProtobufWireFormat(value, maxDepth, depth + 1);
            if (nestedFields.length > 0) {
              interpretedValue = {
                nested_fields: nestedFields,
                length: value.length
              };
            } else {
              // Try as string
              try {
                const decodedStr = value.toString('utf8');
                if (decodedStr.length > 0) {
                  interpretedValue = {
                    as_string: decodedStr,
                    length: value.length
                  };
                }
              } catch {
                interpretedValue = { length: value.length };
              }
            }
          }
        } catch {
          try {
            const decodedStr = value.toString('utf8');
            interpretedValue = {
              as_string: decodedStr,
              length: value.length
            };
          } catch {
            interpretedValue = { length: value.length };
          }
        }
      }

      const wireTypeNames = ['varint', 'fixed64', 'length-delimited', 'start_group', 'end_group', 'fixed32'];
      fields.push({
        field_number: fieldNumber,
        wire_type: wireType,
        wire_type_name: wireType < 6 ? wireTypeNames[wireType] : 'unknown',
        value: interpretedValue
      });
    } catch (e) {
      if (fields.length > 0) {
        break;
      }
      return [];
    }
  }

  return fields;
}

// ============================================================================
// Decryption Functions
// ============================================================================

function decryptAesCtr(data, key, skipBytes = 0) {
  try {
    data = data.slice(skipBytes);
    if (data.length < 16) return null;

    const nonce = data.slice(0, 16);
    const encryptedData = data.slice(16);

    const decipher = crypto.createDecipheriv('aes-128-ctr', key, nonce);
    const decrypted = Buffer.concat([decipher.update(encryptedData), decipher.final()]);
    return decrypted;
  } catch {
    return null;
  }
}

function decryptAesCbc(data, key, skipBytes = 0) {
  try {
    data = data.slice(skipBytes);
    if (data.length < 16) return null;

    const iv = data.slice(0, 16);
    const encryptedData = data.slice(16);

    if (encryptedData.length === 0 || encryptedData.length % 16 !== 0) {
      return null;
    }

    const decipher = crypto.createDecipheriv('aes-128-cbc', key, iv);
    decipher.setAutoPadding(true);
    const decrypted = Buffer.concat([decipher.update(encryptedData), decipher.final()]);
    return decrypted;
  } catch {
    return null;
  }
}

function decryptAesGcm(data, key, skipBytes = 0) {
  try {
    data = data.slice(skipBytes);
    if (data.length < 12) return null;

    const nonce = data.slice(0, 12);
    const encryptedData = data.slice(12);

    if (encryptedData.length < 16) return null;

    const ciphertext = encryptedData.slice(0, -16);
    const tag = encryptedData.slice(-16);

    const decipher = crypto.createDecipheriv('aes-128-gcm', key, nonce);
    decipher.setAuthTag(tag);
    const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
    return decrypted;
  } catch {
    return null;
  }
}

function isValidProtobuf(data, minFields = 1) {
  try {
    const testData = data.slice(0, Math.min(5000, data.length));
    const fields = parseProtobufWireFormat(testData);
    if (!fields || fields.length === 0) return false;
    const validFields = fields.filter(f => f && f.field_number !== undefined);
    return validFields.length >= minFields;
  } catch {
    return false;
  }
}

function decryptFile(filePath, key, verbose = false) {
  const encryptedData = fs.readFileSync(filePath);

  const decryptMethods = [
    { name: 'AES-CTR', func: decryptAesCtr },
    { name: 'AES-CBC', func: decryptAesCbc },
    { name: 'AES-GCM', func: decryptAesGcm }
  ];

  for (const { name, func } of decryptMethods) {
    if (verbose) {
      console.error(`  Trying ${name}...`);
    }

    for (const skip of [0, 1, 2, 4, 8]) {
      const decrypted = func(encryptedData, key, skip);
      if (decrypted) {
        for (const postSkip of [0, 1, 2, 4, 8]) {
          const testData = decrypted.slice(postSkip);
          if (isValidProtobuf(testData)) {
            if (verbose) {
              console.error(`  ✓ Success with ${name} (skip ${skip}, post-skip ${postSkip})`);
            }
            return testData;
          }

          // Check for readable text
          try {
            const textPreview = testData.slice(0, 200).toString('utf8');
            if (textPreview.length > 50 && /^[\x20-\x7E\s]*$/.test(textPreview)) {
              if (verbose) {
                console.error(`  ? ${name} produced readable text (may be valid)`);
              }
              return testData;
            }
          } catch {
            // ignore
          }
        }
      }
    }
  }

  return null;
}

// ============================================================================
// Text Extraction
// ============================================================================

function extractTextFromFields(fields, maxLength = 10000) {
  const texts = [];

  function extractRecursive(fieldList, depth = 0) {
    if (depth > 10) return;
    for (const field of fieldList) {
      if (field && typeof field === 'object') {
        const value = field.value;
        if (value && typeof value === 'object') {
          if (value.as_string) {
            const text = value.as_string;
            if (text && text.trim().length > 5) {
              texts.push(text.slice(0, maxLength));
            }
          }
          if (value.nested_fields) {
            extractRecursive(value.nested_fields, depth + 1);
          }
        } else if (typeof value === 'string' || Buffer.isBuffer(value)) {
          try {
            const text = Buffer.isBuffer(value) ? value.toString('utf8') : value;
            if (text && text.trim().length > 5) {
              texts.push(text.slice(0, maxLength));
            }
          } catch {
            // ignore
          }
        }
      }
    }
  }

  extractRecursive(fields);
  return texts;
}

function extractConversationMessages(fields) {
  const messages = [];
  const texts = extractTextFromFields(fields);

  for (const text of texts) {
    if (text.trim().length < 10) continue;

    // Skip binary-looking data
    const preview = text.slice(0, 100);
    if (!/[\x20-\x7E\s]/.test(preview)) continue;

    messages.push({
      content: text.trim(),
      length: text.length
    });
  }

  return messages;
}

// ============================================================================
// Main Processing
// ============================================================================

function processConversationFile(filePath, key, verbose = false) {
  const result = {
    file: path.basename(filePath),
    path: filePath,
    success: false,
    error: null,
    messages: [],
    metadata: {}
  };

  try {
    const stat = fs.statSync(filePath);
    result.metadata = {
      size: stat.size,
      modified: stat.mtimeMs / 1000
    };

    const decrypted = decryptFile(filePath, key, verbose);
    if (!decrypted) {
      result.error = 'Decryption failed';
      return result;
    }

    result.metadata.decrypted_size = decrypted.length;

    const fields = parseProtobufWireFormat(decrypted);
    if (!fields || fields.length === 0) {
      result.error = 'Could not parse protobuf';
      return result;
    }

    const messages = extractConversationMessages(fields);
    result.messages = messages;
    result.success = true;
    result.metadata.field_count = fields.length;
    result.metadata.message_count = messages.length;
  } catch (e) {
    result.error = e.message;
  }

  return result;
}

function formatConversationOutput(result, formatType = 'json') {
  if (formatType === 'json') {
    return JSON.stringify(result, null, 2);
  } else if (formatType === 'text') {
    const lines = [];
    lines.push(`File: ${result.file}`);
    lines.push(`Status: ${result.success ? 'Success' : 'Failed'}`);
    if (result.error) {
      lines.push(`Error: ${result.error}`);
    }
    lines.push(`Messages: ${result.metadata.message_count || 0}`);
    lines.push('');
    lines.push('='.repeat(70));
    lines.push('CONVERSATION CONTENT');
    lines.push('='.repeat(70));
    lines.push('');

    result.messages.forEach((msg, i) => {
      lines.push(`--- Message ${i + 1} (${msg.length} chars) ---`);
      lines.push(msg.content);
      lines.push('');
    });

    return lines.join('\n');
  }
  return String(result);
}

// ============================================================================
// Interactive Mode
// ============================================================================

function interactiveMode(args) {
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  printHeader('🔓 Antigravity Decryptor - Interactive Mode');
  console.log(`\n${Colors.BOLD}Welcome!${Colors.RESET} This tool decrypts Antigravity IDE conversation files.\n`);

  const prompt = (question) => new Promise((resolve) => rl.question(question, resolve));

  (async () => {
    try {
      if (!args.input) {
        console.log(`${Colors.CYAN}Step 1:${Colors.RESET} Input file or directory`);
        args.input = await prompt('  Enter path to .pb file or directory: ');
        args.input = args.input.trim();
        if (!args.input) {
          printError('No input provided. Exiting.');
          rl.close();
          process.exit(1);
        }
      }

      if (!args.key) {
        console.log(`\n${Colors.CYAN}Step 2:${Colors.RESET} Encryption key`);
        console.log('  You can:');
        console.log('    1. Enter key now (base64 encoded)');
        console.log('    2. Press Enter to try environment variable or Keychain');
        const keyInput = await prompt('  Enter key (or press Enter to auto-detect): ');
        if (keyInput.trim()) {
          args.key = keyInput.trim();
        }
      }

      if (!args.output) {
        console.log(`\n${Colors.CYAN}Step 3:${Colors.RESET} Output location`);
        let defaultOutput;
        if (fs.statSync(args.input).isFile()) {
          defaultOutput = args.input.replace(/\.pb$/, '.json');
        } else {
          defaultOutput = path.join(args.input, 'decrypted');
        }
        console.log(`  Default: ${Colors.DIM}${defaultOutput}${Colors.RESET}`);
        const outputInput = await prompt('  Enter output path (or press Enter for default): ');
        args.output = outputInput.trim() || defaultOutput;
      }

      if (!args.format || args.format === 'json') {
        console.log(`\n${Colors.CYAN}Step 4:${Colors.RESET} Output format`);
        console.log('  1. JSON (default) - Structured data');
        console.log('  2. Text - Human-readable');
        const formatChoice = await prompt('  Choose format (1/2 or press Enter for JSON): ');
        if (formatChoice.trim() === '2') {
          args.format = 'text';
        }
      }

      printHeader('\n🚀 Starting decryption...');
      console.log(`  Input: ${Colors.CYAN}${args.input}${Colors.RESET}`);
      console.log(`  Output: ${Colors.CYAN}${args.output}${Colors.RESET}`);
      console.log(`  Format: ${Colors.CYAN}${args.format}${Colors.RESET}\n`);

      rl.close();
      processWithArgs(args);
    } catch (error) {
      printError(`Error: ${error.message}`);
      rl.close();
      process.exit(1);
    }
  })();
}

// ============================================================================
// CLI Interface
// ============================================================================

function processWithArgs(args) {
  let key = null;
  if (args.key) {
    try {
      key = Buffer.from(args.key, 'base64');
    } catch {
      printError('Invalid key format. Key must be base64 encoded.');
      printInfo('Example: qFl7rbZfqbZoahxeyCwdCg==');
      process.exit(1);
    }
  } else {
    key = getKeyFromKeychain();
    if (!key) {
      key = getKeyFromEnv();
    }
  }

  if (!key) {
    printError('Could not retrieve encryption key.');
    printInfo('You have several options to provide the encryption key:');
    console.error(`  ${Colors.BOLD}1.${Colors.RESET} Use --key option: ${Colors.DIM}node antigravity-decrypt.js file.pb --key "YOUR_KEY"${Colors.RESET}`);
    console.error(`  ${Colors.BOLD}2.${Colors.RESET} Set environment variable: ${Colors.DIM}export ANTIGRAVITY_KEY="YOUR_KEY"${Colors.RESET}`);
    console.error(`  ${Colors.BOLD}3.${Colors.RESET} On macOS: Key is auto-retrieved from Keychain (service: 'Antigravity Safe Storage')`);
    console.error(`\n${Colors.YELLOW}💡 Tip:${Colors.RESET} The key should be base64 encoded (e.g., 'qFl7rbZfqbZoahxeyCwdCg==')`);
    process.exit(1);
  }

  if (args.verbose) {
    printInfo(`Using encryption key: ${key.toString('hex').slice(0, 32)}...`);
  }

  const inputPath = args.input;
  const stat = fs.statSync(inputPath);

  if (stat.isFile()) {
    if (args.verbose) {
      printHeader(`📄 Processing file: ${path.basename(inputPath)}`);
    }

    const result = processConversationFile(inputPath, key, args.verbose);
    const output = formatConversationOutput(result, args.format);

    if (args.output) {
      fs.writeFileSync(args.output, output, 'utf8');
      if (result.success) {
        printSuccess(`Successfully decrypted and saved to: ${args.output}`);
        if (result.metadata.message_count > 0) {
          printInfo(`Extracted ${result.metadata.message_count} messages`);
        }
      } else {
        printError(`Failed to decrypt: ${result.error || 'Unknown error'}`);
      }
    } else {
      console.log(output);
    }
  } else if (stat.isDirectory()) {
    const files = fs.readdirSync(inputPath);
    const pbFiles = files.filter(f => f.endsWith('.pb')).map(f => path.join(inputPath, f));

    if (pbFiles.length === 0) {
      printError(`No .pb files found in ${inputPath}`);
      printInfo(`Looking for files with .pb extension in: ${path.resolve(inputPath)}`);
      process.exit(1);
    }

    printHeader(`📁 Batch Processing: ${pbFiles.length} files found`);

    const outputDir = args.output || path.join(inputPath, 'decrypted');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const results = [];
    let successful = 0;
    let failed = 0;

    pbFiles.forEach((pbFile, i) => {
      if (!args.verbose) {
        const fileName = path.basename(pbFile).slice(0, 30);
        printProgressBar(i, pbFiles.length, 'Progress:', `${fileName}...`);
      } else {
        printInfo(`[${i + 1}/${pbFiles.length}] Processing ${path.basename(pbFile)}...`);
      }

      const result = processConversationFile(pbFile, key, args.verbose);
      results.push(result);

      if (result.success) {
        successful++;
      } else {
        failed++;
      }

      const outputFile = path.join(outputDir, `${path.basename(pbFile, '.pb')}_decrypted.${args.format}`);
      const output = formatConversationOutput(result, args.format);
      fs.writeFileSync(outputFile, output, 'utf8');
    });

    if (!args.verbose) {
      printProgressBar(pbFiles.length, pbFiles.length, 'Progress:', 'Complete!');
    }

    const summaryFile = path.join(outputDir, 'summary.json');
    const totalMessages = results.reduce((sum, r) => sum + r.messages.length, 0);
    fs.writeFileSync(summaryFile, JSON.stringify({
      total_files: pbFiles.length,
      successful,
      failed,
      total_messages: totalMessages,
      files: results
    }, null, 2));

    printHeader('\n📊 Summary');
    console.log(`  ${Colors.GREEN}✓${Colors.RESET} Successful: ${Colors.BOLD}${successful}${Colors.RESET}/${pbFiles.length}`);
    if (failed > 0) {
      console.log(`  ${Colors.RED}✗${Colors.RESET} Failed: ${Colors.BOLD}${failed}${Colors.RESET}/${pbFiles.length}`);
    }
    console.log(`  💬 Total messages extracted: ${Colors.BOLD}${totalMessages}${Colors.RESET}`);
    console.log(`  📂 Output directory: ${Colors.CYAN}${outputDir}${Colors.RESET}`);
    console.log(`  📄 Summary saved to: ${Colors.CYAN}${summaryFile}${Colors.RESET}`);

    if (failed > 0) {
      printWarning(`\n${failed} file(s) failed. Check summary.json for details.`);
    }
  } else {
    printError(`${inputPath} is not a file or directory`);
    printInfo('Please provide a valid .pb file or directory containing .pb files');
    process.exit(1);
  }
}

function main() {
  const args = {
    input: null,
    output: null,
    key: null,
    format: 'json',
    verbose: false,
    interactive: false,
    version: false,
    help: false
  };

  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg === '--help' || arg === '-h') {
      args.help = true;
    } else if (arg === '--version') {
      args.version = true;
    } else if (arg === '--interactive' || arg === '-i') {
      args.interactive = true;
    } else if (arg === '--verbose' || arg === '-v') {
      args.verbose = true;
    } else if (arg === '--key' || arg === '-k') {
      args.key = process.argv[++i];
    } else if (arg === '--output' || arg === '-o') {
      args.output = process.argv[++i];
    } else if (arg === '--format' || arg === '-f') {
      args.format = process.argv[++i];
    } else if (!arg.startsWith('-')) {
      args.input = arg;
    }
  }

  if (args.help) {
    console.log(`${Colors.BOLD}🔓 Antigravity IDE Conversation Decryptor${Colors.RESET} v${VERSION}

Decrypt and extract human-readable conversations from Antigravity IDE's encrypted .pb files.

${Colors.BOLD}Usage:${Colors.RESET}
  antigravity-decrypt <input> [options]
  node antigravity-decrypt.js <input> [options]

${Colors.BOLD}Arguments:${Colors.RESET}
  input                      Input .pb file or directory containing .pb files

${Colors.BOLD}Options:${Colors.RESET}
  -o, --output <path>        Output file or directory (default: stdout for files, ./decrypted for dirs)
  -k, --key <key>            Encryption key (base64 encoded). Alternative: use ANTIGRAVITY_KEY env var
  -f, --format <format>      Output format: json or text (default: json)
  -v, --verbose              Show detailed processing information
  -i, --interactive          Interactive mode with prompts
  --version                  Show version number
  -h, --help                 Show this help message

${Colors.BOLD}Examples:${Colors.RESET}
  ${Colors.CYAN}# Decrypt a single file${Colors.RESET}
  node antigravity-decrypt.js conversation.pb --output conversation.json
  
  ${Colors.CYAN}# Decrypt all files in a directory with progress tracking${Colors.RESET}
  node antigravity-decrypt.js ./conversations --output ./decrypted
  
  ${Colors.CYAN}# Use custom key (base64 encoded)${Colors.RESET}
  node antigravity-decrypt.js conversation.pb --key "qFl7rbZfqbZoahxeyCwdCg=="
  
  ${Colors.CYAN}# Set key via environment variable${Colors.RESET}
  export ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg=="
  node antigravity-decrypt.js conversation.pb
  
  ${Colors.CYAN}# Get human-readable text output${Colors.RESET}
  node antigravity-decrypt.js conversation.pb --format text --output conversation.txt
  
  ${Colors.CYAN}# Interactive mode for beginners${Colors.RESET}
  node antigravity-decrypt.js --interactive

${Colors.BOLD}Key Management:${Colors.RESET}
  Priority order: --key argument → ANTIGRAVITY_KEY env var → macOS Keychain

${Colors.BOLD}Need Help?${Colors.RESET}
  See README.md or visit: https://github.com/arashz/antigravity_decryptor
`);
    process.exit(0);
  }

  if (args.version) {
    console.log(VERSION);
    process.exit(0);
  }

  if (args.interactive || !args.input) {
    interactiveMode(args);
  } else {
    processWithArgs(args);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  decryptFile,
  processConversationFile,
  extractConversationMessages,
  parseProtobufWireFormat
};
