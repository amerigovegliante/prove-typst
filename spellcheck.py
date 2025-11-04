#!/usr/bin/env python3
"""
Spellcheck Typst files using a text dictionary.
Usage: python spellcheck_typst.py <dictionary.txt> <file1.typ> [file2.typ ...]
       python spellcheck_typst.py <dictionary.txt> --all  (checks all .typ files)
"""

import sys
import re
from pathlib import Path


def load_dictionary(dict_path):
    """Load dictionary from text file into a set."""
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            words = {line.strip().lower() for line in f if line.strip()}
        print(f"Loaded {len(words)} words from dictionary")
        return words
    except FileNotFoundError:
        print(f"Error: Dictionary file '{dict_path}' not found")
        sys.exit(1)


def extract_text_from_typst(content):
    """Extract readable text from Typst content, removing markup."""
    # Remove line comments
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove Typst function calls
    content = re.sub(r'#[a-zA-Z_][a-zA-Z0-9_]*(?:\[.*?\]|\(.*?\))?', '', content, flags=re.DOTALL)
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # Remove inline code
    content = re.sub(r'`[^`]+`', '', content)
    # Remove URLs
    content = re.sub(r'https?://[^\s\)]+', '', content)
    # Remove Typst special characters
    content = re.sub(r'[#\[\]{}*_~=<>|\\]', ' ', content)
    return content


def extract_words(text):
    """Extract words from text."""
    words = re.findall(r"[a-zA-ZàèéìòùÀÈÉÌÒÙáéíóúÁÉÍÓÚäëïöüÄËÏÖÜâêîôûÂÊÎÔÛ']+", text)
    return [w.lower() for w in words if len(w) > 1]


def spellcheck_file(filepath, dictionary):
    """Spellcheck a single Typst file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return False
    except UnicodeDecodeError:
        print(f"Error: Cannot decode '{filepath}' as UTF-8")
        return False
    
    text = extract_text_from_typst(content)
    words = extract_words(text)
    misspelled = {word for word in words if word not in dictionary}
    
    if misspelled:
        print(f"\n❌ Misspellings in {filepath}:")
        for word in sorted(misspelled):
            print(f"  - {word}")
        return False
    else:
        print(f"✓ No misspellings found in {filepath}")
        return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python spellcheck_typst.py <dictionary.txt> <file1.typ> [file2.typ ...]")
        print("       python spellcheck_typst.py <dictionary.txt> --all")
        print("\nExamples:")
        print("  python spellcheck_typst.py combined_dict.txt document.typ")
        print("  python spellcheck_typst.py combined_dict.txt --all")
        sys.exit(1)
    
    dict_path = sys.argv[1]
    dictionary = load_dictionary(dict_path)
    
    if sys.argv[2] == '--all':
        typst_files = [str(p) for p in Path('.').rglob('*.typ')]
        if not typst_files:
            print("No .typ files found")
            sys.exit(0)
    else:
        typst_files = sys.argv[2:]
    
    all_passed = all(spellcheck_file(f, dictionary) for f in typst_files)
    
    if all_passed:
        print("\n✅ All files passed spellcheck!")
        sys.exit(0)
    else:
        print("\n⚠️  Some files have spelling errors")
        sys.exit(1)


if __name__ == "__main__":
    main()