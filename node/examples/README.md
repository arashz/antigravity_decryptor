# Node.js Examples

This directory contains practical examples of using the Antigravity Decryptor with Node.js.

## Available Examples

### basic-usage.js

Demonstrates how to use the decryptor module programmatically:
- Decrypt a single file
- Process files and get structured results
- Batch process multiple files
- Key management from different sources

```bash
# Run the examples
node examples/basic-usage.js

# With custom key
ANTIGRAVITY_KEY="qFl7rbZfqbZoahxeyCwdCg==" node examples/basic-usage.js
```

## Requirements

All examples require:
- Node.js 16+ (no external dependencies needed)
- Valid encryption key (via environment variable or command-line)

## Getting Started

1. Set your encryption key:
```bash
export ANTIGRAVITY_KEY="your_base64_key_here"
```

2. Run an example:
```bash
node examples/basic-usage.js
```

## Using Examples as Templates

These examples are designed to be copied and modified for your own projects:

```javascript
// Copy the pattern from basic-usage.js
const { processConversationFile } = require('./antigravity-decrypt');

const key = Buffer.from(process.env.ANTIGRAVITY_KEY, 'base64');
const result = processConversationFile('myfile.pb', key);

if (result.success) {
  console.log(`Extracted ${result.metadata.message_count} messages`);
}
```

## Integration Patterns

### Pattern 1: Single File Processing

```javascript
const { processConversationFile } = require('./antigravity-decrypt');
const fs = require('fs');

function processFile(inputPath, outputPath, key) {
  const result = processConversationFile(inputPath, key);
  
  if (result.success) {
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    return true;
  }
  
  console.error(`Failed: ${result.error}`);
  return false;
}
```

### Pattern 2: Batch Processing with Promises

```javascript
const { processConversationFile } = require('./antigravity-decrypt');
const fs = require('fs').promises;
const path = require('path');

async function batchProcess(directory, key) {
  const files = await fs.readdir(directory);
  const pbFiles = files.filter(f => f.endsWith('.pb'));
  
  const results = await Promise.all(
    pbFiles.map(file => {
      const filePath = path.join(directory, file);
      return processConversationFile(filePath, key);
    })
  );
  
  return results;
}
```

### Pattern 3: Stream Processing

```javascript
const { decryptFile, parseProtobufWireFormat } = require('./antigravity-decrypt');
const { Transform } = require('stream');

class DecryptTransform extends Transform {
  constructor(key, options) {
    super(options);
    this.key = key;
  }
  
  _transform(chunk, encoding, callback) {
    try {
      const decrypted = decryptFile(chunk, this.key);
      if (decrypted) {
        this.push(decrypted);
      }
      callback();
    } catch (error) {
      callback(error);
    }
  }
}
```

## Tips

1. **Error Handling**: Always check `result.success` before accessing `result.messages`
2. **Key Security**: Never hardcode keys in your source code. Use environment variables or secure config files
3. **Batch Processing**: Process files in chunks if you have many files to avoid memory issues
4. **Progress Tracking**: Use progress bars or logging for long-running batch operations
5. **Output Format**: Choose JSON for programmatic processing, text for human readability

## Troubleshooting

**Example script fails with "Cannot find module"**
- Make sure you're in the `node` directory when running examples
- The script uses relative paths to import the main module

**"No .pb files found"**
- Examples look for files in expected locations
- Modify the file paths in the example scripts to match your setup

**"Could not retrieve encryption key"**
- Set the `ANTIGRAVITY_KEY` environment variable
- Or modify the example to use your key source

## More Help

See the main README.md for:
- Installation instructions
- Key management options
- Troubleshooting guide
- API documentation
