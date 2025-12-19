#!/usr/bin/env node

/**
 * Basic usage examples for Antigravity Decryptor (Node.js)
 * 
 * This script demonstrates how to use the decryptor module programmatically.
 */

const { decryptFile, processConversationFile, extractConversationMessages, parseProtobufWireFormat } = require('../antigravity-decrypt');
const fs = require('fs');
const path = require('path');

// Example 1: Decrypt a single file with a known key
function example1() {
  console.log('Example 1: Decrypt a single file');
  console.log('='.repeat(50));
  
  // Your base64-encoded encryption key
  const keyB64 = process.env.ANTIGRAVITY_KEY || 'qFl7rbZfqbZoahxeyCwdCg==';
  const key = Buffer.from(keyB64, 'base64');
  
  // Path to your .pb file
  const filePath = './conversation.pb';
  
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    console.log('Please provide a valid .pb file to test with.\n');
    return;
  }
  
  try {
    // Decrypt the file
    const decrypted = decryptFile(filePath, key, true);
    
    if (decrypted) {
      console.log(`✓ Successfully decrypted ${filePath}`);
      console.log(`  Decrypted size: ${decrypted.length} bytes`);
      
      // Parse protobuf
      const fields = parseProtobufWireFormat(decrypted);
      console.log(`  Protobuf fields found: ${fields.length}`);
      
      // Extract messages
      const messages = extractConversationMessages(fields);
      console.log(`  Messages extracted: ${messages.length}`);
      
      if (messages.length > 0) {
        console.log('\nFirst message preview:');
        console.log(messages[0].content.slice(0, 200) + '...');
      }
    } else {
      console.log('✗ Decryption failed');
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

// Example 2: Process a file and get structured result
function example2() {
  console.log('Example 2: Process file with full result');
  console.log('='.repeat(50));
  
  const keyB64 = process.env.ANTIGRAVITY_KEY || 'qFl7rbZfqbZoahxeyCwdCg==';
  const key = Buffer.from(keyB64, 'base64');
  const filePath = './conversation.pb';
  
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filePath}`);
    console.log('Please provide a valid .pb file to test with.\n');
    return;
  }
  
  try {
    // Process the file - returns structured result
    const result = processConversationFile(filePath, key, false);
    
    console.log(`File: ${result.file}`);
    console.log(`Success: ${result.success}`);
    
    if (result.success) {
      console.log(`Messages: ${result.metadata.message_count}`);
      console.log(`Total characters: ${result.messages.reduce((sum, m) => sum + m.length, 0)}`);
      
      // Save to JSON
      const outputPath = './conversation_output.json';
      fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
      console.log(`✓ Saved result to ${outputPath}`);
    } else {
      console.log(`Error: ${result.error}`);
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

// Example 3: Batch process multiple files
function example3() {
  console.log('Example 3: Batch process directory');
  console.log('='.repeat(50));
  
  const keyB64 = process.env.ANTIGRAVITY_KEY || 'qFl7rbZfqbZoahxeyCwdCg==';
  const key = Buffer.from(keyB64, 'base64');
  const directory = './conversations';
  
  if (!fs.existsSync(directory)) {
    console.log(`Directory not found: ${directory}`);
    console.log('Please create a directory with .pb files to test with.\n');
    return;
  }
  
  try {
    const files = fs.readdirSync(directory);
    const pbFiles = files.filter(f => f.endsWith('.pb'));
    
    if (pbFiles.length === 0) {
      console.log('No .pb files found in directory\n');
      return;
    }
    
    console.log(`Found ${pbFiles.length} .pb files`);
    
    let successful = 0;
    let failed = 0;
    const results = [];
    
    pbFiles.forEach((file, index) => {
      const filePath = path.join(directory, file);
      console.log(`[${index + 1}/${pbFiles.length}] Processing ${file}...`);
      
      const result = processConversationFile(filePath, key, false);
      results.push(result);
      
      if (result.success) {
        successful++;
        console.log(`  ✓ ${result.metadata.message_count} messages extracted`);
      } else {
        failed++;
        console.log(`  ✗ Failed: ${result.error}`);
      }
    });
    
    console.log('\nSummary:');
    console.log(`  Successful: ${successful}/${pbFiles.length}`);
    console.log(`  Failed: ${failed}/${pbFiles.length}`);
    
    // Save summary
    const summary = {
      total_files: pbFiles.length,
      successful,
      failed,
      total_messages: results.reduce((sum, r) => sum + r.messages.length, 0),
      files: results
    };
    
    const summaryPath = './batch_summary.json';
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
    console.log(`✓ Summary saved to ${summaryPath}`);
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

// Example 4: Custom key from different sources
function example4() {
  console.log('Example 4: Key management');
  console.log('='.repeat(50));
  
  // Method 1: From environment variable
  if (process.env.ANTIGRAVITY_KEY) {
    const key1 = Buffer.from(process.env.ANTIGRAVITY_KEY, 'base64');
    console.log('✓ Key loaded from ANTIGRAVITY_KEY environment variable');
    console.log(`  Key (hex): ${key1.toString('hex').slice(0, 32)}...`);
  } else {
    console.log('⚠ ANTIGRAVITY_KEY environment variable not set');
  }
  
  // Method 2: From string literal (not recommended for production)
  const keyB64 = 'qFl7rbZfqbZoahxeyCwdCg==';
  const key2 = Buffer.from(keyB64, 'base64');
  console.log('\n✓ Key loaded from string literal');
  console.log(`  Key (hex): ${key2.toString('hex').slice(0, 32)}...`);
  
  // Method 3: From file (good for config files)
  const configExample = {
    key: 'qFl7rbZfqbZoahxeyCwdCg==',
    inputDir: './conversations',
    outputDir: './decrypted'
  };
  
  console.log('\n✓ Example config file format:');
  console.log(JSON.stringify(configExample, null, 2));
  
  console.log('\n');
}

// Main
function main() {
  console.log('\n╔═══════════════════════════════════════════════════╗');
  console.log('║   Antigravity Decryptor - Node.js Examples      ║');
  console.log('╚═══════════════════════════════════════════════════╝\n');
  
  // Run examples
  example1();
  example2();
  example3();
  example4();
  
  console.log('Done! Check the generated files:');
  console.log('  - conversation_output.json');
  console.log('  - batch_summary.json');
}

if (require.main === module) {
  main();
}
