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
    
    # Configuration constants
    MAX_DSL_ITERATIONS = 50  # Maximum iterations for DSL resolution
    MAX_ATTEMPTS_MULTIPLIER = 10  # Multiplier for max attempts in sentence generation
    
    def __init__(self, grammar_file: str = "grammar_rules.yaml", seed: Optional[int] = None):
        """
        Initialize the generator with grammar rules.
        
        Args:
            grammar_file: Path to YAML file containing grammar rules
            seed: Random seed for reproducibility (optional)
        """
        self.grammar = self._load_grammar(grammar_file)
        self.context = {}  # Context memory for OS, Vendor, Version, etc.
        self.variables = {}  # Variable storage for consistency (e.g., {VAR:name})
        self.used_sentences = set()  # Track used sentences to avoid repetition
        self.seed = seed
        self.seed_multipliers = {}  # Store seed multipliers for sub-generators
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
        - {R min-max SEED:mult} - Random range with seed multiplier
        - {O opt1|opt2|opt3} - OR choice
        - {M2 item1|item2|item3} - Multi-pick (2 unique items)
        - {W item1:weight1|item2:weight2} - Weighted choice
        - {C CATEGORY} - Category call
        - {C2 CATEGORY} - Multi-pick from category
        - {VAR:name value} - Store value in variable 'name'
        - {VAR:name} - Retrieve stored variable 'name'
        
        Args:
            text: Text containing DSL expressions in curly braces
            
        Returns:
            Text with DSL expressions resolved
        """
        
        def find_matching_brace(text, start_pos):
            """Find the matching closing brace for an opening brace at start_pos."""
            if text[start_pos] != '{':
                return -1
            
            depth = 0
            for i in range(start_pos, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        return i
            return -1
        
        def resolve_expression(expr):
            """Resolve a single DSL expression."""
            expr = expr.strip()
            
            # Variable storage: {VAR:name value} or {VAR:name}
            if expr.startswith('VAR:'):
                parts = expr[4:].strip().split(None, 1)
                var_name = parts[0]
                if len(parts) > 1:
                    # Store value and resolve it: {VAR:cve CVE-2021-{R 1000-9999}}
                    value = parts[1]
                    # Check if this variable is already stored (to avoid re-resolving)
                    if var_name not in self.variables:
                        # Resolve any nested expressions in the value
                        resolved_value = self._resolve_dsl(value)
                        self.variables[var_name] = resolved_value
                        return resolved_value
                    else:
                        # Variable already exists, return its stored value
                        return self.variables[var_name]
                else:
                    # Retrieve value: {VAR:cve}
                    if var_name in self.variables:
                        return self.variables[var_name]
                    return '{' + expr + '}'
            
            # Random range: {R 100-999} or {R 100-999 SEED:mult}
            if expr.startswith('R '):
                range_part = expr[2:].strip()
                try:
                    # Check if there's a seed multiplier
                    seed_mult = None
                    if 'SEED:' in range_part:
                        parts = range_part.split('SEED:')
                        range_part = parts[0].strip()
                        seed_mult = parts[1].strip()
                    
                    start, end = map(int, range_part.split('-'))
                    
                    # If seed multiplier is provided, use it to create a sub-generator
                    if seed_mult and self.seed is not None:
                        # Create a unique seed based on base seed and multiplier
                        # Always use hash for consistency regardless of multiplier type
                        mult_value = int(seed_mult) if seed_mult.isdigit() else seed_mult
                        sub_seed = hash((self.seed, mult_value))
                        # Store or retrieve the value for this seed multiplier
                        if seed_mult not in self.seed_multipliers:
                            temp_state = random.getstate()
                            random.seed(sub_seed)
                            self.seed_multipliers[seed_mult] = str(random.randint(start, end))
                            random.setstate(temp_state)
                        return self.seed_multipliers[seed_mult]
                    else:
                        return str(random.randint(start, end))
                except (ValueError, IndexError):
                    return '{' + expr + '}'  # Return original if invalid
            
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
                    return '{' + expr + '}'
            
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
                    return '{' + expr + '}'
            
            # Category call: {C CATEGORY} or {C2 CATEGORY}
            elif expr.startswith('C'):
                # Check if it's multi-pick from category like {C2 ACTION}
                if len(expr) > 1 and expr[1].isdigit():
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
                        return '{' + expr + '}'
                else:
                    # Simple category call {C CATEGORY}
                    category = expr[1:].strip()
                    if category in self.grammar:
                        return self._weighted_choice(self.grammar[category])
            
            return '{' + expr + '}'  # Return original if not matched
        
        # Process text using brace matching
        result = []
        i = 0
        max_iterations = self.MAX_DSL_ITERATIONS
        iterations = 0
        
        while i < len(text) and iterations < max_iterations:
            if text[i] == '{':
                # Find matching closing brace
                close_pos = find_matching_brace(text, i)
                if close_pos != -1:
                    # Extract and resolve the expression
                    expr = text[i+1:close_pos]
                    resolved = resolve_expression(expr)
                    result.append(resolved)
                    i = close_pos + 1
                else:
                    # No matching brace, treat as literal
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        # Join and check if we need another iteration (for nested expressions)
        new_text = ''.join(result)
        if new_text != text and '{' in new_text:
            iterations += 1
            if iterations < max_iterations:
                return self._resolve_dsl(new_text)
        
        return new_text
    
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
        # Reset state for each generation to avoid carryover
        self.reset_generation_state()
        
        if use_post:
            return self.generate_post(apply_mutations)
        
        if use_format:
            return self.generate_format(apply_mutations)
        
        if num_sentences is None:
            num_sentences = random.randint(4, 10)
        
        # Reset sentence tracking for this generation
        self.used_sentences = set()
        
        sentences = []
        max_attempts = num_sentences * self.MAX_ATTEMPTS_MULTIPLIER  # Limit attempts to avoid infinite loops
        attempts = 0
        
        while len(sentences) < num_sentences and attempts < max_attempts:
            attempts += 1
            
            # Clear context for each new sentence group (but keep some continuity)
            if random.random() < 0.3:
                self.context = {}
            
            # Start with the sentence rule
            sentence = "<sentence>"
            
            # Recursively expand until only terminals remain
            sentence = self._expand_rule(sentence)
            
            # Clean up any remaining artifacts
            sentence = sentence.strip()
            
            # Ensure sentence ends with a period
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            
            # Check if this sentence is unique (before mutations)
            sentence_normalized = sentence.lower().strip()
            if sentence_normalized not in self.used_sentences and sentence:
                self.used_sentences.add(sentence_normalized)
                
                # Apply mutations if enabled
                if apply_mutations:
                    sentence = self._apply_mutations(sentence)
                
                sentences.append(sentence)
        
        return ' '.join(sentences)
    
    def set_seed(self, seed: int):
        """Set random seed for reproducibility."""
        self.seed = seed
        random.seed(seed)
        # Reset state-dependent attributes
        self.variables = {}
        self.seed_multipliers = {}
        self.used_sentences = set()
    
    def get_context(self) -> Dict[str, str]:
        """Get current context memory."""
        return self.context.copy()
    
    def reset_generation_state(self):
        """Reset generation state for a fresh generation."""
        self.variables = {}
        self.seed_multipliers = {}
        self.used_sentences = set()


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
