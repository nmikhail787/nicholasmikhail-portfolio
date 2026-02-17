#!/usr/bin/env python3
"""
Validation script to check submission completeness.
"""
import os
import json
import sys

def check_file_exists(path):
    """Check if a file exists."""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {path}")
    return exists

def validate_output_file(path):
    """Validate the output JSONL file."""
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            
        print(f"\n📊 Output File Validation:")
        print(f"  • Total documents: {len(lines)}")
        
        # Validate each line is valid JSON
        for i, line in enumerate(lines[:3]):  # Check first 3
            doc = json.loads(line)
            required_fields = ['url', 'title', 'body_text', 'fetched_at', 'metadata']
            missing = [f for f in required_fields if f not in doc]
            if missing:
                print(f"  ❌ Document {i+1} missing fields: {missing}")
                return False
        
        print(f"  ✅ All documents have required fields")
        print(f"  ✅ Valid JSONL format")
        return True
        
    except Exception as e:
        print(f"  ❌ Error validating output: {e}")
        return False

def main():
    print("="*70)
    print("🔍 SUBMISSION VALIDATION")
    print("="*70)
    
    print("\n📁 Required Files:")
    all_exist = True
    
    # Core files
    all_exist &= check_file_exists('scraper.py')
    all_exist &= check_file_exists('analytics.py')
    all_exist &= check_file_exists('requirements.txt')
    all_exist &= check_file_exists('README.md')
    
    # Source files
    all_exist &= check_file_exists('src/__init__.py')
    all_exist &= check_file_exists('src/config.py')
    all_exist &= check_file_exists('src/crawler.py')
    all_exist &= check_file_exists('src/extractor.py')
    all_exist &= check_file_exists('src/enricher.py')
    all_exist &= check_file_exists('src/storage.py')
    all_exist &= check_file_exists('src/pipeline.py')
    
    # Tests
    all_exist &= check_file_exists('tests/__init__.py')
    all_exist &= check_file_exists('tests/test_extractor.py')
    
    # Output
    all_exist &= check_file_exists('output/scraped_data.jsonl')
    
    # Validate output file
    if os.path.exists('output/scraped_data.jsonl'):
        all_exist &= validate_output_file('output/scraped_data.jsonl')
    
    print("\n" + "="*70)
    if all_exist:
        print("✅ ALL CHECKS PASSED - Ready to submit!")
    else:
        print("❌ SOME CHECKS FAILED - Review above")
        sys.exit(1)
    print("="*70)

if __name__ == '__main__':
    main()