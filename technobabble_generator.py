#!/usr/bin/env python3
"""
Technobabble Generator - A rule-based hacker shitpost generator
Generates plausible-sounding but meaningless security technobabble
"""

import yaml
import random
import re
from typing import Dict, List, Tuple, Optional, Any


class TechnobabbleGenerator:
    """
    A rule-based text generator using recursive grammar rules with weighted random selection.
    """
    
    def __init__(self, grammar_file: str = "grammar_rules.yaml", seed: Optional[int] = None):
        """
        Initialize the generator with grammar rules.
        
        Args:
            grammar_file: Path to YAML file containing grammar rules
            seed: Random seed for reproducibility (optional)
        """
        self.grammar = self._load_grammar(grammar_file)
        self.context = {}  # Context memory for OS, Vendor, Version, etc.
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def _load_grammar(self, grammar_file: str) -> Dict[str, List[Tuple[int, str]]]:
        """Load grammar rules from YAML file."""
        with open(grammar_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _weighted_choice(self, options: List[Tuple[int, str]]) -> str:
        """
        Select an option based on weights.
        
        Args:
            options: List of (weight, text) tuples
            
        Returns:
            Selected text based on weighted random choice
        """
        weights = [w for w, _ in options]
        texts = [t for _, t in options]
        return random.choices(texts, weights=weights, k=1)[0]
    
    def _expand_rule(self, text: str, depth: int = 0, max_depth: int = 50) -> str:
        """
        Recursively expand non-terminal symbols in text until only terminals remain.
        
        Args:
            text: Text containing potential non-terminal symbols
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Fully expanded text with only terminal symbols
        """
        if depth > max_depth:
            return text
        
        # Find all non-terminals in angle brackets
        pattern = r'<([^>]+)>'
        match = re.search(pattern, text)
        
        if not match:
            # No more non-terminals, return the text
            return text
        
        # Get the non-terminal symbol
        symbol = match.group(1)
        
        # Check if we have a rule for this symbol
        if symbol in self.grammar:
            # Expand the symbol
            expansion = self._weighted_choice(self.grammar[symbol])
            
            # Store context for certain symbols
            if symbol in ['vendor', 'os', 'product', 'version_number']:
                self.context[symbol] = expansion
            
            # Replace the non-terminal with its expansion
            text = text[:match.start()] + expansion + text[match.end():]
            
            # Continue expanding recursively
            return self._expand_rule(text, depth + 1, max_depth)
        else:
            # Unknown symbol, leave it as is and continue with remaining symbols
            # Replace with empty string or keep the brackets
            text = text[:match.start()] + text[match.end():]
            return self._expand_rule(text, depth + 1, max_depth)
    
    def _apply_mutations(self, sentence: str) -> str:
        """
        Apply sentence-level mutations for variety.
        
        Args:
            sentence: Original sentence
            
        Returns:
            Mutated sentence
        """
        # Randomly capitalize certain security terms
        security_terms = ['critical', 'vulnerability', 'exploit', 'remote', 'authentication']
        for term in security_terms:
            if term in sentence.lower() and random.random() < 0.3:
                sentence = re.sub(
                    r'\b' + term + r'\b', 
                    term.upper(), 
                    sentence, 
                    flags=re.IGNORECASE,
                    count=1
                )
        
        # Sometimes add urgency markers
        if random.random() < 0.15:
            urgency = random.choice(['[URGENT] ', '[CRITICAL] ', '[ZERO-DAY] '])
            sentence = urgency + sentence
        
        return sentence
    
    def generate(self, 
                 num_sentences: int = None,
                 theme: Optional[str] = None,
                 apply_mutations: bool = True) -> str:
        """
        Generate technobabble text.
        
        Args:
            num_sentences: Number of sentences to generate (random 4-10 if None)
            theme: Optional theme mode (currently unused, for future expansion)
            apply_mutations: Whether to apply sentence mutations
            
        Returns:
            Generated technobabble text
        """
        if num_sentences is None:
            num_sentences = random.randint(4, 10)
        
        sentences = []
        
        for _ in range(num_sentences):
            # Clear context for each new sentence group (but keep some continuity)
            if random.random() < 0.3:
                self.context = {}
            
            # Start with the sentence rule
            sentence = "<sentence>"
            
            # Recursively expand until only terminals remain
            sentence = self._expand_rule(sentence)
            
            # Apply mutations if enabled
            if apply_mutations:
                sentence = self._apply_mutations(sentence)
            
            # Clean up any remaining artifacts
            sentence = sentence.strip()
            
            # Ensure sentence ends with a period
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            
            sentences.append(sentence)
        
        return ' '.join(sentences)
    
    def set_seed(self, seed: int):
        """Set random seed for reproducibility."""
        self.seed = seed
        random.seed(seed)
    
    def get_context(self) -> Dict[str, str]:
        """Get current context memory."""
        return self.context.copy()


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate plausible-sounding security technobabble'
    )
    parser.add_argument(
        '-n', '--num-sentences',
        type=int,
        default=None,
        help='Number of sentences to generate (default: random 4-10)'
    )
    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--no-mutations',
        action='store_true',
        help='Disable sentence mutations'
    )
    parser.add_argument(
        '-g', '--grammar',
        type=str,
        default='grammar_rules.yaml',
        help='Path to grammar rules file (default: grammar_rules.yaml)'
    )
    parser.add_argument(
        '--theme',
        type=str,
        default=None,
        help='Theme mode (for future use)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = TechnobabbleGenerator(
            grammar_file=args.grammar,
            seed=args.seed
        )
        
        output = generator.generate(
            num_sentences=args.num_sentences,
            theme=args.theme,
            apply_mutations=not args.no_mutations
        )
        
        print(output)
        
        # Show seed if it was set
        if args.seed is not None:
            print(f"\n[Seed: {args.seed}]", file=__import__('sys').stderr)
            
    except FileNotFoundError as e:
        print(f"Error: Grammar file not found: {e}", file=__import__('sys').stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
