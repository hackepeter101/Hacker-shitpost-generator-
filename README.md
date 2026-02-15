# Hacker-shitpost-generator-

A rule-based technobabble generator that creates plausible-sounding but meaningless security text using recursive grammar rules with weighted random selection.

## Features

- **Recursive Grammar Rules**: Uses YAML-defined grammar rules that expand recursively until only terminal symbols remain
- **Weighted Random Selection**: Each grammar rule has weighted options for more natural variation
- **Context Memory**: Maintains context for OS, Vendor, Version, and Product across sentence generation
- **Reproducibility**: Supports random seed for generating identical output
- **Sentence Mutations**: Optional mutations add urgency markers and capitalize security terms
- **Configurable Output**: Generate 4-10 sentences (default) or specify exact count
- **Theme Support**: Extensible architecture for future theme modes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hackepeter101/Hacker-shitpost-generator-.git
cd Hacker-shitpost-generator-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate random technobabble (4-10 sentences):
```bash
python3 technobabble_generator.py
```

### Advanced Options

Generate specific number of sentences:
```bash
python3 technobabble_generator.py -n 7
```

Use seed for reproducibility:
```bash
python3 technobabble_generator.py --seed 42
```

Disable sentence mutations:
```bash
python3 technobabble_generator.py --no-mutations
```

Use custom grammar file:
```bash
python3 technobabble_generator.py -g custom_rules.yaml
```

### Python API

```python
from technobabble_generator import TechnobabbleGenerator

# Create generator
gen = TechnobabbleGenerator(seed=42)

# Generate technobabble
output = gen.generate(num_sentences=5)
print(output)

# Get context memory
context = gen.get_context()
print(context)
```

## Example Output

```
The vulnerable code path involves string concatenation in the SSL/TLS implementation. 
We discovered a high-severity cross-site scripting vulnerability in x64 systems version 2.4.x. 
The CVSS 6.5 rating reflects the high-severity nature of this vulnerability. 
Organizations should immediately patch their Linux kernel deployments. 
[URGENT] A proof-of-concept was published demonstrating privilege escalation.
```

## Grammar Rules

Grammar rules are defined in `grammar_rules.yaml` using the following format:

```yaml
rule_name:
  - [weight, "expansion with <other_rules>"]
  - [weight, "alternative expansion"]
```

Non-terminal symbols are enclosed in angle brackets `<symbol>` and are recursively expanded until only terminal text remains.

## Testing

Run the test suite:
```bash
python3 -m unittest test_technobabble_generator.py -v
```

## How It Works

1. **Grammar Loading**: Loads weighted grammar rules from YAML file
2. **Rule Expansion**: Recursively expands non-terminal symbols using weighted random selection
3. **Context Tracking**: Maintains context for consistency (e.g., same vendor across sentences)
4. **Mutation Application**: Optionally applies sentence-level mutations for variety
5. **Output Assembly**: Combines generated sentences into coherent technobabble

## Security Notice

This generator creates **fictional, meaningless security text** for entertainment purposes only. The output:
- Contains no real vulnerabilities or exploits
- Should not be used for actual security research
- Is purely for generating plausible-sounding nonsense

## License

MIT License - See repository for details.

## Contributing

Contributions welcome! Please submit pull requests or open issues for:
- Additional grammar rules
- New theme modes
- Bug fixes
- Feature enhancements