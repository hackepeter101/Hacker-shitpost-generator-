#!/usr/bin/env python3
"""
Examples demonstrating various features of the Technobabble Generator
"""

from technobabble_generator import TechnobabbleGenerator


def example_basic():
    """Basic usage example."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Generation")
    print("=" * 80)
    
    gen = TechnobabbleGenerator()
    output = gen.generate(num_sentences=5)
    print(output)
    print()


def example_reproducible():
    """Reproducibility with seed example."""
    print("=" * 80)
    print("EXAMPLE 2: Reproducible Generation (with seed)")
    print("=" * 80)
    
    seed = 42
    print(f"Using seed: {seed}\n")
    
    # First generation
    gen1 = TechnobabbleGenerator(seed=seed)
    output1 = gen1.generate(num_sentences=4)
    print("First generation:")
    print(output1)
    print()
    
    # Second generation with same seed
    gen2 = TechnobabbleGenerator(seed=seed)
    output2 = gen2.generate(num_sentences=4)
    print("Second generation (should be identical):")
    print(output2)
    print()
    
    print(f"Outputs are identical: {output1 == output2}")
    print()


def example_no_mutations():
    """Generation without mutations example."""
    print("=" * 80)
    print("EXAMPLE 3: Generation Without Mutations")
    print("=" * 80)
    
    gen = TechnobabbleGenerator(seed=123)
    output = gen.generate(num_sentences=6, apply_mutations=False)
    print(output)
    print("\n(Note: No [URGENT], [CRITICAL], or capitalized terms)")
    print()


def example_context_memory():
    """Context memory example."""
    print("=" * 80)
    print("EXAMPLE 4: Context Memory")
    print("=" * 80)
    
    gen = TechnobabbleGenerator(seed=456)
    
    for i in range(3):
        output = gen.generate(num_sentences=2)
        context = gen.get_context()
        print(f"Generation {i+1}:")
        print(output)
        print(f"Context: {context}")
        print()


def example_variable_length():
    """Variable length generation example."""
    print("=" * 80)
    print("EXAMPLE 5: Variable Length Generation")
    print("=" * 80)
    
    gen = TechnobabbleGenerator(seed=789)
    
    for num in [4, 7, 10]:
        output = gen.generate(num_sentences=num)
        print(f"{num} sentences:")
        print(output)
        print()


def example_batch_generation():
    """Batch generation example."""
    print("=" * 80)
    print("EXAMPLE 6: Batch Generation (Multiple Reports)")
    print("=" * 80)
    
    gen = TechnobabbleGenerator()
    
    for i in range(3):
        print(f"\n--- Report {i+1} ---")
        output = gen.generate()
        print(output)
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("TECHNOBABBLE GENERATOR - EXAMPLES")
    print("=" * 80 + "\n")
    
    example_basic()
    example_reproducible()
    example_no_mutations()
    example_context_memory()
    example_variable_length()
    example_batch_generation()
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
