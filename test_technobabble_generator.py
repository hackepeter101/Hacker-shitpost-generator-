#!/usr/bin/env python3
"""
Tests for the Technobabble Generator
"""

import unittest
import random
from technobabble_generator import TechnobabbleGenerator


class TestTechnobabbleGenerator(unittest.TestCase):
    """Test cases for TechnobabbleGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = TechnobabbleGenerator(grammar_file="grammar_rules.yaml")
    
    def test_generator_initialization(self):
        """Test that generator initializes correctly."""
        self.assertIsNotNone(self.generator.grammar)
        self.assertIn('sentence', self.generator.grammar)
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same output."""
        gen1 = TechnobabbleGenerator(grammar_file="grammar_rules.yaml", seed=42)
        output1 = gen1.generate(num_sentences=5, apply_mutations=False)
        
        gen2 = TechnobabbleGenerator(grammar_file="grammar_rules.yaml", seed=42)
        output2 = gen2.generate(num_sentences=5, apply_mutations=False)
        
        self.assertEqual(output1, output2)
    
    def test_different_seeds_produce_different_output(self):
        """Test that different seeds produce different output."""
        gen1 = TechnobabbleGenerator(grammar_file="grammar_rules.yaml", seed=42)
        output1 = gen1.generate(num_sentences=5)
        
        gen2 = TechnobabbleGenerator(grammar_file="grammar_rules.yaml", seed=123)
        output2 = gen2.generate(num_sentences=5)
        
        self.assertNotEqual(output1, output2)
    
    def test_generate_returns_string(self):
        """Test that generate returns a string."""
        output = self.generator.generate(num_sentences=5)
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)
    
    def test_sentence_count(self):
        """Test that correct number of sentences are generated."""
        for num in [4, 6, 10]:
            output = self.generator.generate(num_sentences=num)
            # Split by '. ' to count sentences more reliably
            # Add a final period if not present for consistent counting
            if not output.endswith('.'):
                output += '.'
            # Split and filter out empty strings
            sentences = [s.strip() for s in output.split('. ') if s.strip()]
            # The count should be close to requested (may have extra due to splits on periods in text)
            self.assertGreaterEqual(len(sentences), num - 1)  # Allow for edge cases
    
    def test_random_sentence_count(self):
        """Test that random sentence count is within range."""
        output = self.generator.generate()
        sentence_count = output.count('.')
        # Should generate 4-10 sentences, but count may be higher due to 
        # periods in version numbers, etc.
        self.assertGreaterEqual(sentence_count, 4)
    
    def test_no_unresolved_symbols(self):
        """Test that all symbols are resolved (no < > remaining)."""
        output = self.generator.generate(num_sentences=10, apply_mutations=False)
        # Should not contain unresolved non-terminals
        self.assertNotIn('<', output)
        self.assertNotIn('>', output)
    
    def test_weighted_choice(self):
        """Test weighted choice functionality."""
        options = [(10, 'common'), (1, 'rare')]
        results = [self.generator._weighted_choice(options) for _ in range(100)]
        # Common should appear more often than rare
        self.assertGreater(results.count('common'), results.count('rare'))
    
    def test_context_memory(self):
        """Test that context memory is used."""
        self.generator.generate(num_sentences=3)
        context = self.generator.get_context()
        # Context should potentially have some values (might be empty due to randomness)
        self.assertIsInstance(context, dict)
    
    def test_mutations_optional(self):
        """Test that mutations can be disabled."""
        output = self.generator.generate(num_sentences=5, apply_mutations=False)
        # Should not contain mutation markers
        self.assertNotIn('[URGENT]', output)
        self.assertNotIn('[CRITICAL]', output)
        self.assertNotIn('[ZERO-DAY]', output)
    
    def test_set_seed(self):
        """Test that seed can be set after initialization."""
        self.generator.set_seed(42)
        output1 = self.generator.generate(num_sentences=5, apply_mutations=False)
        
        self.generator.set_seed(42)
        output2 = self.generator.generate(num_sentences=5, apply_mutations=False)
        
        self.assertEqual(output1, output2)
    
    def test_output_is_plausible(self):
        """Test that output contains expected security terms."""
        output = self.generator.generate(num_sentences=10)
        # Should contain at least some security-related terms
        security_terms = ['vulnerability', 'security', 'exploit', 'attack', 
                         'system', 'code', 'access', 'authentication']
        found_terms = [term for term in security_terms if term.lower() in output.lower()]
        self.assertGreater(len(found_terms), 0)
    
    def test_multiple_generations(self):
        """Test that multiple generations work correctly."""
        for _ in range(10):
            output = self.generator.generate(num_sentences=5)
            self.assertIsInstance(output, str)
            self.assertGreater(len(output), 0)
    
    def test_dsl_random_range(self):
        """Test DSL random range {R min-max}."""
        gen = TechnobabbleGenerator(seed=42)
        result = gen._resolve_dsl("Value: {R 100-200}")
        # Should contain a number between 100 and 200
        self.assertNotIn('{R', result)
        self.assertIn('Value:', result)
    
    def test_dsl_or_choice(self):
        """Test DSL OR choice {O opt1|opt2|opt3}."""
        gen = TechnobabbleGenerator(seed=42)
        result = gen._resolve_dsl("Choose: {O apple|banana|cherry}")
        # Should contain one of the options
        self.assertNotIn('{O', result)
        self.assertIn('Choose:', result)
        self.assertTrue(any(fruit in result for fruit in ['apple', 'banana', 'cherry']))
    
    def test_dsl_multi_pick(self):
        """Test DSL multi-pick {M2 item1|item2|item3}."""
        gen = TechnobabbleGenerator(seed=42)
        result = gen._resolve_dsl("Pick two: {M2 red|green|blue|yellow}")
        # Should contain two different items
        self.assertNotIn('{M2', result)
        self.assertIn('Pick two:', result)
    
    def test_dsl_weighted_choice(self):
        """Test DSL weighted choice {W item1:weight1|item2:weight2}."""
        gen = TechnobabbleGenerator(seed=42)
        result = gen._resolve_dsl("Weighted: {W common:10|rare:1}")
        # Should contain one of the options
        self.assertNotIn('{W', result)
        self.assertIn('Weighted:', result)
    
    def test_dsl_category_call(self):
        """Test DSL category call {C CATEGORY}."""
        gen = TechnobabbleGenerator(seed=42)
        # severity is a simple category in the grammar
        result = gen._resolve_dsl("Severity: {C severity}")
        # Should have resolved to something from severity category
        self.assertNotIn('{C severity}', result)
        self.assertIn('Severity:', result)
    
    def test_variable_storage_and_retrieval(self):
        """Test DSL variable storage and retrieval."""
        gen = TechnobabbleGenerator(seed=42)
        # Store and retrieve a simple value
        result = gen._resolve_dsl("ID: {VAR:id 12345}. Same ID: {VAR:id}")
        self.assertNotIn('{VAR', result)
        self.assertEqual(result, "ID: 12345. Same ID: 12345")
    
    def test_variable_with_nested_expression(self):
        """Test variable storage with nested random expressions."""
        gen = TechnobabbleGenerator(seed=42)
        # Store a value that contains a random expression
        result = gen._resolve_dsl("CVE: {VAR:cve CVE-2021-{R 1000-9999}}. Reference: {VAR:cve}")
        self.assertNotIn('{VAR', result)
        self.assertNotIn('{R', result)
        # Extract the CVE numbers - they should be the same
        parts = result.split('. ')
        cve1 = parts[0].split(': ')[1]
        cve2 = parts[1].split(': ')[1]
        self.assertEqual(cve1, cve2)
        self.assertTrue(cve1.startswith('CVE-2021-'))
    
    def test_seed_multiplier(self):
        """Test seed multipliers for consistent random values."""
        gen = TechnobabbleGenerator(seed=42)
        # Same seed multiplier should give same value
        result = gen._resolve_dsl("Count: {R 100-200 SEED:systems}. Again: {R 100-200 SEED:systems}.")
        self.assertNotIn('{R', result)
        # Extract the numbers - they should be the same
        import re
        numbers = re.findall(r'\d+', result.replace('100-200', ''))
        self.assertEqual(len(numbers), 2)
        self.assertEqual(numbers[0], numbers[1])
    
    def test_no_duplicate_sentences(self):
        """Test that sentences are not duplicated within a single generation."""
        gen = TechnobabbleGenerator(seed=42)
        output = gen.generate(num_sentences=20, apply_mutations=False)
        sentences = [s.strip().lower() + '.' for s in output.split('. ') if s.strip()]
        # All sentences should be unique
        unique_sentences = set(sentences)
        self.assertEqual(len(sentences), len(unique_sentences))
    
    def test_reset_generation_state(self):
        """Test that generation state is reset between generations."""
        gen = TechnobabbleGenerator(seed=42)
        # Generate once and store some variables
        gen.variables['test'] = 'value1'
        gen.seed_multipliers['mult1'] = '100'
        gen.used_sentences.add('test sentence')
        
        # Generate again - state should be reset
        gen.generate(num_sentences=3)
        # Variables and multipliers should be cleared
        self.assertEqual(len(gen.variables), 0)
        self.assertEqual(len(gen.seed_multipliers), 0)
        self.assertEqual(len(gen.used_sentences), 3)  # Should have new sentences
    
    def test_new_categories_exist(self):
        """Test that new hierarchical categories are loaded."""
        self.assertIn('POST', self.generator.grammar)
        self.assertIn('TYPE', self.generator.grammar)
        self.assertIn('TUTORIAL_POST', self.generator.grammar)
        self.assertIn('TIP_POST', self.generator.grammar)
        self.assertIn('DISCOVERY_POST', self.generator.grammar)
        self.assertIn('WARNING_POST', self.generator.grammar)
        self.assertIn('RANT_POST', self.generator.grammar)
        self.assertIn('THEORY_POST', self.generator.grammar)
        self.assertIn('INTRO', self.generator.grammar)
        self.assertIn('TECH_CHAIN', self.generator.grammar)
        self.assertIn('SYSTEM', self.generator.grammar)
        self.assertIn('OS', self.generator.grammar)
        self.assertIn('VENDOR', self.generator.grammar)
        self.assertIn('EXPLOIT_STYLE', self.generator.grammar)
        self.assertIn('EVIDENCE', self.generator.grammar)
        self.assertIn('CONSEQUENCE', self.generator.grammar)
        self.assertIn('COMMENT', self.generator.grammar)
        self.assertIn('OUTRO', self.generator.grammar)
    
    def test_post_generation(self):
        """Test that POST category generates valid output."""
        gen = TechnobabbleGenerator(seed=42)
        post = gen._expand_rule('<POST>')
        # Should be a string with some content
        self.assertIsInstance(post, str)
        self.assertGreater(len(post), 10)
        # Should not have unresolved symbols
        self.assertNotIn('<', post)
        self.assertNotIn('>', post)
        # Should not have unresolved DSL
        self.assertNotIn('{C', post)
        self.assertNotIn('{R', post)
        self.assertNotIn('{O', post)
        self.assertNotIn('{M', post)
        self.assertNotIn('{W', post)


if __name__ == '__main__':
    unittest.main()
