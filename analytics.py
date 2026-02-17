#!/usr/bin/env python3
"""
Analytics script to analyze scraped data.
"""
import argparse
import json
import sys
from collections import Counter


def load_documents(file_path: str):
    """Load documents from JSONL file."""
    documents = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    doc = json.loads(line)
                    documents.append(doc)
        return documents
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading documents: {e}")
        sys.exit(1)


def analyze_documents(documents):
    """Analyze document collection."""
    if not documents:
        print("No documents found!")
        return
    
    total_docs = len(documents)
    
    # Word count stats
    word_counts = [doc['metadata']['word_count'] for doc in documents]
    avg_words = sum(word_counts) / len(word_counts)
    min_words = min(word_counts)
    max_words = max(word_counts)
    total_words = sum(word_counts)
    
    # Character count
    char_counts = [doc['metadata']['char_count'] for doc in documents]
    total_chars = sum(char_counts)
    
    # Reading time
    reading_times = [doc['metadata']['reading_time_minutes'] for doc in documents]
    total_reading_time = sum(reading_times)
    
    # Language distribution
    languages = [doc['metadata']['language'] for doc in documents]
    lang_dist = Counter(languages)
    
    # Content type distribution
    content_types = [doc['metadata']['content_type'] for doc in documents]
    content_dist = Counter(content_types)
    
    # Category analysis
    all_categories = []
    for doc in documents:
        all_categories.extend(doc['metadata']['categories'])
    top_categories = Counter(all_categories).most_common(10)
    
    # References and links
    total_refs = sum(doc['metadata']['references_count'] for doc in documents)
    avg_refs = total_refs / total_docs
    total_links = sum(doc['metadata']['links_count'] for doc in documents)
    avg_links = total_links / total_docs
    
    # Print analysis
    print("\n" + "=" * 70)
    print("📊 COLLECTION ANALYSIS")
    print("=" * 70)
    
    print(f"\n📚 Total Documents: {total_docs}")
    
    print("\n📝 Word Count Statistics:")
    print(f"  • Average:  {avg_words:,.0f} words")
    print(f"  • Minimum:  {min_words:,} words")
    print(f"  • Maximum:  {max_words:,} words")
    print(f"  • Total:    {total_words:,} words")
    
    print("\n💭 Character Count:")
    print(f"  • Total:    {total_chars:,} characters")
    
    print("\n⏱️  Reading Time:")
    print(f"  • Total:    {total_reading_time:.1f} minutes ({total_reading_time/60:.1f} hours)")
    
    print("\n🌍 Language Distribution:")
    for lang, count in lang_dist.items():
        percentage = 100 * count / total_docs
        print(f"  • {lang}: {count} documents ({percentage:.1f}%)")
    
    print("\n📄 Content Type Distribution:")
    for ctype, count in content_dist.items():
        percentage = 100 * count / total_docs
        print(f"  • {ctype}: {count} documents ({percentage:.1f}%)")
    
    print("\n🏷️  Top 10 Categories:")
    for category, count in top_categories:
        print(f"  • {category}: {count} occurrences")
    
    print("\n🔗 Links & References:")
    print(f"  • Average references per page: {avg_refs:.1f}")
    print(f"  • Average links per page: {avg_links:.1f}")
    
    print("\n📋 Sample Documents:")
    print("-" * 70)
    for i, doc in enumerate(documents[:3], 1):
        print(f"\n{i}. {doc['title']}")
        print(f"   URL: {doc['url']}")
        print(f"   Words: {doc['metadata']['word_count']}, "
              f"Type: {doc['metadata']['content_type']}")
    print("-" * 70)
    
    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze scraped document collection'
    )
    
    parser.add_argument(
        '--input',
        default='output/scraped_data.jsonl',
        help='Input JSONL file to analyze'
    )
    
    args = parser.parse_args()
    
    print(f"Loading documents from: {args.input}")
    documents = load_documents(args.input)
    
    print(f"Loaded {len(documents)} documents")
    
    analyze_documents(documents)


if __name__ == '__main__':
    main()