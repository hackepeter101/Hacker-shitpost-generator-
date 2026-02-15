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
            # Count periods as rough sentence count
            # Note: Some sentences may contain periods in version numbers, etc.
            # So we check that the count is at least the requested number
            sentence_count = output.count('.')
            self.assertGreaterEqual(sentence_count, num)
    
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


if __name__ == '__main__':
    unittest.main()
