#!/usr/bin/env python3
"""
Example: Advanced Conversation Analysis
========================================

This example shows how to analyze decrypted conversations:
- Extract statistics
- Search for keywords
- Generate reports
- Export in various formats
"""

import sys
import json
import base64
from pathlib import Path
from collections import Counter
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from antigravity_decrypt import process_conversation_file


class ConversationAnalyzer:
    """Analyze conversation files and generate insights."""
    
    def __init__(self, key: bytes):
        self.key = key
        self.results = []
    
    def analyze_file(self, file_path: str) -> dict:
        """Analyze a single conversation file."""
        result = process_conversation_file(file_path, self.key)
        
        if not result['success']:
            return result
        
        # Add analysis
        messages = result['messages']
        analysis = {
            'total_messages': len(messages),
            'total_chars': sum(msg['length'] for msg in messages),
            'avg_message_length': sum(msg['length'] for msg in messages) / len(messages) if messages else 0,
            'shortest_message': min(msg['length'] for msg in messages) if messages else 0,
            'longest_message': max(msg['length'] for msg in messages) if messages else 0,
        }
        
        # Word count
        all_text = ' '.join(msg['content'] for msg in messages)
        words = all_text.split()
        analysis['total_words'] = len(words)
        analysis['avg_words_per_message'] = len(words) / len(messages) if messages else 0
        
        # Most common words (excluding short words)
        word_freq = Counter(w.lower() for w in words if len(w) > 4)
        analysis['top_10_words'] = word_freq.most_common(10)
        
        result['analysis'] = analysis
        return result
    
    def analyze_directory(self, dir_path: str) -> list:
        """Analyze all conversation files in a directory."""
        directory = Path(dir_path)
        pb_files = list(directory.glob("*.pb"))
        
        print(f"📁 Analyzing {len(pb_files)} conversation files...")
        print()
        
        for i, pb_file in enumerate(pb_files, 1):
            print(f"[{i}/{len(pb_files)}] {pb_file.name}...", end=' ')
            result = self.analyze_file(str(pb_file))
            self.results.append(result)
            
            if result['success']:
                print(f"✓ {result['analysis']['total_messages']} messages")
            else:
                print(f"✗ Failed")
        
        return self.results
    
    def search_keyword(self, keyword: str) -> list:
        """Search for keyword across all analyzed conversations."""
        matches = []
        
        for result in self.results:
            if not result['success']:
                continue
            
            for i, msg in enumerate(result['messages']):
                if keyword.lower() in msg['content'].lower():
                    matches.append({
                        'file': result['file'],
                        'message_index': i + 1,
                        'content_preview': msg['content'][:200],
                        'full_length': msg['length']
                    })
        
        return matches
    
    def generate_report(self) -> dict:
        """Generate comprehensive analysis report."""
        successful = [r for r in self.results if r['success']]
        
        if not successful:
            return {'error': 'No successful analyses'}
        
        total_messages = sum(r['analysis']['total_messages'] for r in successful)
        total_chars = sum(r['analysis']['total_chars'] for r in successful)
        total_words = sum(r['analysis']['total_words'] for r in successful)
        
        report = {
            'summary': {
                'total_files': len(self.results),
                'successful_files': len(successful),
                'failed_files': len(self.results) - len(successful),
                'total_messages': total_messages,
                'total_characters': total_chars,
                'total_words': total_words,
                'avg_messages_per_file': total_messages / len(successful) if successful else 0,
                'avg_chars_per_message': total_chars / total_messages if total_messages else 0,
            },
            'files': []
        }
        
        # File details
        for result in successful:
            report['files'].append({
                'name': result['file'],
                'messages': result['analysis']['total_messages'],
                'characters': result['analysis']['total_chars'],
                'words': result['analysis']['total_words'],
                'avg_message_length': round(result['analysis']['avg_message_length'], 2),
            })
        
        # Sort by message count
        report['files'].sort(key=lambda x: x['messages'], reverse=True)
        
        return report
    
    def export_report(self, output_path: str, format: str = 'json'):
        """Export analysis report to file."""
        report = self.generate_report()
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'text':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("ANTIGRAVITY CONVERSATION ANALYSIS REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                f.write("SUMMARY\n")
                f.write("-" * 70 + "\n")
                for key, value in report['summary'].items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                
                f.write("\n\nFILE DETAILS\n")
                f.write("-" * 70 + "\n")
                for file_info in report['files']:
                    f.write(f"\n{file_info['name']}\n")
                    f.write(f"  Messages: {file_info['messages']}\n")
                    f.write(f"  Characters: {file_info['characters']}\n")
                    f.write(f"  Words: {file_info['words']}\n")
                    f.write(f"  Avg message length: {file_info['avg_message_length']}\n")
        
        print(f"✓ Report exported to: {output_path}")


def main():
    """Main function for the analysis example."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Antigravity conversation files")
    parser.add_argument('--input', '-i', required=True, help='Input directory with .pb files')
    parser.add_argument('--output', '-o', default='analysis_report.json', help='Output report file')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Report format')
    parser.add_argument('--key', '-k', help='Encryption key (base64 encoded)')
    parser.add_argument('--search', '-s', help='Search for keyword in conversations')
    
    args = parser.parse_args()
    
    # Get key
    if args.key:
        key = base64.b64decode(args.key)
    else:
        import os
        key_b64 = os.environ.get('ANTIGRAVITY_KEY')
        if not key_b64:
            print("Error: No encryption key provided!")
            print("Use --key option or set ANTIGRAVITY_KEY environment variable")
            sys.exit(1)
        key = base64.b64decode(key_b64)
    
    # Analyze
    analyzer = ConversationAnalyzer(key)
    analyzer.analyze_directory(args.input)
    
    print()
    print("=" * 70)
    
    # Search if requested
    if args.search:
        print(f"\n🔍 Searching for '{args.search}'...")
        matches = analyzer.search_keyword(args.search)
        print(f"Found {len(matches)} matches:")
        for match in matches[:10]:  # Show first 10
            print(f"  - {match['file']} (message {match['message_index']})")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")
    
    # Export report
    print()
    analyzer.export_report(args.output, args.format)
    
    # Print summary
    report = analyzer.generate_report()
    if 'summary' in report:
        print("\n📊 Analysis Summary:")
        print(f"  Files processed: {report['summary']['successful_files']}")
        print(f"  Total messages: {report['summary']['total_messages']}")
        print(f"  Total words: {report['summary']['total_words']}")
        print(f"  Avg messages per file: {report['summary']['avg_messages_per_file']:.1f}")


if __name__ == "__main__":
    main()
