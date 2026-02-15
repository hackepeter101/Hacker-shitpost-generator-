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
    
    def _resolve_dsl(self, text: str) -> str:
        """
        Resolve custom DSL expressions in text.
        Supports:
        - {R min-max} - Random range
        - {O opt1|opt2|opt3} - OR choice
        - {M2 item1|item2|item3} - Multi-pick (2 unique items)
        - {W item1:weight1|item2:weight2} - Weighted choice
        - {C CATEGORY} - Category call
        - {C2 CATEGORY} - Multi-pick from category
        
        Args:
            text: Text containing DSL expressions in curly braces
            
        Returns:
            Text with DSL expressions resolved
        """
        # Pattern to match {COMMAND ...}
        pattern = r'\{([^}]+)\}'
        
        def resolve_expression(match):
            expr = match.group(1).strip()
            
            # Random range: {R 100-999}
            if expr.startswith('R '):
                range_part = expr[2:].strip()
                try:
                    start, end = map(int, range_part.split('-'))
                    return str(random.randint(start, end))
                except (ValueError, IndexError):
                    return match.group(0)  # Return original if invalid
            
            # OR choice: {O opt1|opt2|opt3}
            elif expr.startswith('O '):
                options_part = expr[2:].strip()
                options = [opt.strip() for opt in options_part.split('|')]
                return random.choice(options)
            
            # Multi-pick: {M2 item1|item2|item3} or {MN item1|item2|item3}
            elif expr.startswith('M') and ' ' in expr:
                parts = expr.split(' ', 1)
                try:
                    count = int(parts[0][1:])  # Extract number from M2, M3, etc.
                    items_part = parts[1].strip()
                    items = [item.strip() for item in items_part.split('|')]
                    # Pick 'count' unique items
                    if count > len(items):
                        count = len(items)
                    selected = random.sample(items, count)
                    return ' '.join(selected)
                except (ValueError, IndexError):
                    return match.group(0)
            
            # Weighted choice: {W item1:weight1|item2:weight2}
            elif expr.startswith('W '):
                options_part = expr[2:].strip()
                try:
                    items = []
                    weights = []
                    for option in options_part.split('|'):
                        item, weight = option.strip().rsplit(':', 1)
                        items.append(item.strip())
                        weights.append(float(weight))
                    return random.choices(items, weights=weights, k=1)[0]
                except (ValueError, IndexError):
                    return match.group(0)
            
            # Category call: {C CATEGORY} or {C2 CATEGORY}
            elif expr.startswith('C'):
                # Check if it's multi-pick from category like {C2 ACTION}
                if expr[1:2].isdigit():
                    try:
                        count = int(expr[1])
                        category = expr[2:].strip()
                        if category in self.grammar:
                            # Pick 'count' unique items from category
                            options = [text for _, text in self.grammar[category]]
                            if count > len(options):
                                count = len(options)
                            selected = random.sample(options, count)
                            return ' '.join(selected)
                    except (ValueError, IndexError):
                        return match.group(0)
                else:
                    # Simple category call {C CATEGORY}
                    category = expr[1:].strip()
                    if category in self.grammar:
                        return self._weighted_choice(self.grammar[category])
            
            return match.group(0)  # Return original if not matched
        
        # Keep resolving until no more expressions (for nested expressions)
        max_iterations = 20
        for _ in range(max_iterations):
            new_text = re.sub(pattern, resolve_expression, text)
            if new_text == text:
                break
            text = new_text
        
        return text
    
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
        
        # First, resolve any DSL expressions (they might generate angle bracket symbols)
        text = self._resolve_dsl(text)
        
        # Find all non-terminals in angle brackets
        pattern = r'<([^>]+)>'
        match = re.search(pattern, text)
        
        if not match:
            # No more non-terminals, return the text
            return text
        
        # Get the non-terminal symbol
        symbol = match.group(1)
        
        # Check if this is a random number range (e.g., <random:1-100>)
        if symbol.startswith('random:'):
            range_part = symbol.split(':', 1)[1]
            try:
                start, end = map(int, range_part.split('-'))
                random_num = str(random.randint(start, end))
                text = text[:match.start()] + random_num + text[match.end():]
                return self._expand_rule(text, depth + 1, max_depth)
            except (ValueError, IndexError):
                # Invalid format, skip it
                text = text[:match.start()] + text[match.end():]
                return self._expand_rule(text, depth + 1, max_depth)
        
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
    
    def generate_format(self, apply_mutations: bool = True) -> str:
        """
        Generate a formatted post using format templates.
        
        Format templates are higher-level structures that combine multiple
        sentences into structured posts (threads, tutorials, reports, etc.)
        
        Args:
            apply_mutations: Whether to apply sentence mutations
            
        Returns:
            Generated formatted post
        """
        # Start with the format rule
        post = "<format>"
        
        # Recursively expand until only terminals remain
        post = self._expand_rule(post)
        
        # Apply mutations to individual sentences if enabled
        if apply_mutations:
            # Split by newlines and apply mutations to lines that look like sentences
            lines = post.split('\n')
            mutated_lines = []
            for line in lines:
                # Only apply mutations to lines that look like sentences (not headers/footers)
                if line.strip() and not line.strip().startswith(('🧵', '📚', '🚨', '⚠️', '🔴', 'Thread', 'THREAD', 'Story', 'Daily', 'What I', 'Today\'s', 'Another day', 'Flexing', 'POV:', 'Friendly')):
                    line = self._apply_mutations(line)
                mutated_lines.append(line)
            post = '\n'.join(mutated_lines)
        
        return post.strip()
    
    def generate_post(self, apply_mutations: bool = False) -> str:
        """
        Generate a complete post using the new POST hierarchical structure.
        
        This uses the new category system with TYPE, INTRO, TECH_CHAIN, 
        EVIDENCE, CONSEQUENCE, COMMENT, and OUTRO.
        
        Args:
            apply_mutations: Whether to apply sentence mutations
            
        Returns:
            Generated post
        """
        # Start with the POST rule
        post = "<POST>"
        
        # Recursively expand until only terminals remain
        post = self._expand_rule(post)
        
        # Apply mutations if enabled
        if apply_mutations:
            lines = post.split('\n')
            mutated_lines = []
            for line in lines:
                if line.strip() and not line.strip().startswith(('🚨', '⚠️', '🔴', '```')):
                    line = self._apply_mutations(line)
                mutated_lines.append(line)
            post = '\n'.join(mutated_lines)
        
        return post.strip()
    
    def generate(self, 
                 num_sentences: int = None,
                 theme: Optional[str] = None,
                 apply_mutations: bool = True,
                 use_format: bool = False,
                 use_post: bool = False) -> str:
        """
        Generate technobabble text.
        
        Args:
            num_sentences: Number of sentences to generate (random 4-10 if None)
            theme: Optional theme mode (currently unused, for future expansion)
            apply_mutations: Whether to apply sentence mutations
            use_format: Whether to use format templates instead of plain sentences
            use_post: Whether to use the new POST hierarchical structure
            
        Returns:
            Generated technobabble text
        """
        if use_post:
            return self.generate_post(apply_mutations)
        
        if use_format:
            return self.generate_format(apply_mutations)
        
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
    import sys
    
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
    parser.add_argument(
        '-f', '--format',
        action='store_true',
        help='Use format templates (threads, tutorials, reports, etc.)'
    )
    parser.add_argument(
        '-p', '--post',
        action='store_true',
        help='Use new POST hierarchical structure (with TYPE, INTRO, TECH_CHAIN, etc.)'
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
            apply_mutations=not args.no_mutations,
            use_format=args.format,
            use_post=args.post
        )
        
        print(output)
        
        # Show seed if it was set
        if args.seed is not None:
            print(f"\n[Seed: {args.seed}]", file=sys.stderr)
            
    except FileNotFoundError as e:
        print(f"Error: Grammar file not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
