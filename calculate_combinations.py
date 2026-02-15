#!/usr/bin/env python3
"""
Calculate the total number of possible sentence combinations in the grammar.
This gives a rough estimate of the variety the generator can produce.
"""

import yaml
from typing import Dict, List, Tuple, Set
import re


def load_grammar(grammar_file: str = "grammar_rules.yaml") -> Dict[str, List[Tuple[int, str]]]:
    """Load grammar rules from YAML file."""
    with open(grammar_file, 'r') as f:
        return yaml.safe_load(f)


def get_non_terminals(text: str) -> Set[str]:
    """Extract all non-terminal symbols from text."""
    pattern = r'<([^>]+)>'
    return set(re.findall(pattern, text))


def calculate_combinations_recursive(symbol: str, grammar_dict: dict, max_depth: int = 20, depth: int = 0, visited: set = None) -> int:
    """
    Calculate the number of possible combinations for a given symbol.
    
    This is a rough estimate that counts unique paths through the grammar tree.
    Due to recursion and context dependencies, actual variety may differ.
    
    Note: visited is an internal implementation detail for tracking recursion.
    """
    if visited is None:
        visited = set()
    
    # Prevent infinite recursion
    if symbol in visited or depth > max_depth:
        return 1
    
    if symbol not in grammar_dict:
        return 1  # Terminal symbol
    
    # Mark as visited
    visited = visited.copy()
    visited.add(symbol)
    
    total = 0
    rules = grammar_dict[symbol]
    
    for weight, expansion in rules:
        # Find all non-terminals in this expansion
        non_terminals = get_non_terminals(expansion)
        
        if not non_terminals:
            # This is a terminal expansion
            total += 1
        else:
            # Calculate combinations for this expansion
            expansion_combos = 1
            for nt in non_terminals:
                nt_combos = calculate_combinations_recursive(nt, grammar_dict, max_depth, depth + 1, visited)
                expansion_combos *= nt_combos
            total += expansion_combos
    
    return total


def main():
    """Calculate and display statistics about the grammar."""
    grammar = load_grammar()
    
    print("=" * 80)
    print("HACKER SHITPOST GENERATOR - COMBINATION STATISTICS")
    print("=" * 80)
    print()
    
    # Count rules and options
    total_rules = len(grammar)
    total_options = sum(len(rules) for rules in grammar.values())
    
    print(f"📊 Grammar Statistics:")
    print(f"   - Total rule categories: {total_rules}")
    print(f"   - Total individual options: {total_options}")
    print()
    
    # Calculate average options per category
    avg_options = total_options / total_rules
    print(f"   - Average options per category: {avg_options:.1f}")
    print()
    
    # Show top-level sentence types
    print(f"📝 Sentence Format Types:")
    sentence_rules = grammar.get('sentence', [])
    print(f"   - Available sentence formats: {len(sentence_rules)}")
    print()
    
    # Count major categories (50+ items)
    large_cats = [(name, len(rules)) for name, rules in grammar.items() if len(rules) >= 45]
    large_cats.sort(key=lambda x: x[1], reverse=True)
    
    print(f"🎯 Categories with 45+ Options:")
    for name, count in large_cats:
        print(f"   - {name}: {count} options")
    print()
    
    # Calculate rough estimate of sentence combinations
    # This is a simplified calculation due to recursion complexity
    print(f"💥 Estimated Combinations:")
    print(f"   Note: These are rough estimates due to grammar recursion and context.")
    print()
    
    try:
        sentence_combos = calculate_combinations_recursive('sentence', grammar, max_depth=5)
        print(f"   - Top-level sentence combinations: ~{sentence_combos:,}")
        print()
        
        # Calculate for a typical 5-sentence output
        five_sentence_combos = sentence_combos ** 5
        print(f"   - Possible 5-sentence outputs: ~{five_sentence_combos:,.2e}")
        print()
        
        # Calculate for typical 4-10 sentence range
        min_combos = sentence_combos ** 4
        max_combos = sentence_combos ** 10
        print(f"   - Range for 4-10 sentence outputs:")
        print(f"     • Minimum (4 sentences): ~{min_combos:,.2e}")
        print(f"     • Maximum (10 sentences): ~{max_combos:,.2e}")
        print()
        
    except Exception as e:
        print(f"   - Complex calculation (error: {e})")
        print(f"   - But with {total_options} total options across {total_rules} categories,")
        print(f"     the variety is MASSIVE! 🚀")
        print()
        
        # Simple estimate based on average branching
        simple_estimate = avg_options ** 5  # Rough estimate
        print(f"   - Simple estimate (avg branching): ~{simple_estimate:,.2e} combinations")
        print()
    
    # Show some example categories
    print(f"🔥 Sample Categories (showing variety):")
    sample_cats = ['vulnerability_type', 'hacker_tool', 'attack_vector', 'component']
    for cat in sample_cats:
        if cat in grammar:
            count = len(grammar[cat])
            samples = [text for _, text in grammar[cat][:3]]
            print(f"   - {cat} ({count} options)")
            for sample in samples:
                print(f"      • {sample}")
    print()
    
    print("=" * 80)
    print("💪 CONCLUSION: This generator can create BILLIONS of unique shitposts! 💪")
    print("=" * 80)


if __name__ == '__main__':
    main()
