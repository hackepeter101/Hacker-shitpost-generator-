# Hacker-shitpost-generator-

A rule-based technobabble generator that creates plausible-sounding but meaningless security text using recursive grammar rules with weighted random selection. Perfect for generating memy hacker shitposts that sound like an 11-year-old who just discovered the wrong side of TikTok! 🚀

## Features

- **Recursive Grammar Rules**: Uses YAML-defined grammar rules that expand recursively until only terminal symbols remain
- **Weighted Random Selection**: Each grammar rule has weighted options for more natural variation
- **Context Memory**: Maintains context for OS, Vendor, Version, and Product across sentence generation
- **Reproducibility**: Supports random seed for generating identical output
- **Sentence Mutations**: Optional mutations add urgency markers and capitalize security terms
- **Configurable Output**: Generate 4-10 sentences (default) or specify exact count
- **Theme Support**: Extensible architecture for future theme modes
- **MASSIVE Variety**: 1,496 individual options across 48 categories with 14 different sentence formats
- **Script Kiddie Mode**: Generates memy content like a wannabe hacker who just watched too many TikTok hacking videos

## Stats

- **📊 Total rule categories**: 48
- **📝 Total individual options**: 1,496
- **🎯 Categories with 50 items**: 25 (including vulnerability types, hacker tools, attack vectors, and more!)
- **🔥 Sentence format types**: 14 (instructions, discoveries, boasts, tutorials, flexes, warnings, and more!)
- **💥 Estimated combinations**: BILLIONS of unique shitposts possible!

Run `python3 calculate_combinations.py` to see detailed statistics about all the possible combinations.

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

Generate formatted posts (threads, tutorials, reports):
```bash
python3 technobabble_generator.py --format
```

### Python API

```python
from technobabble_generator import TechnobabbleGenerator

# Create generator
gen = TechnobabbleGenerator(seed=42)

# Generate plain technobabble sentences
output = gen.generate(num_sentences=5)
print(output)

# Generate formatted posts (threads, tutorials, etc.)
formatted = gen.generate(use_format=True)
print(formatted)
print(output)

# Get context memory
context = gen.get_context()
print(context)
```

## Example Output

### Classic Technobabble
```
The vulnerable code path involves string concatenation in the SSL/TLS implementation. 
We discovered a high-severity cross-site scripting vulnerability in x64 systems version 2.4.x. 
The CVSS 6.5 rating reflects the high-severity nature of this vulnerability. 
Organizations should immediately patch their Linux kernel deployments. 
[URGENT] A proof-of-concept was published demonstrating privilege escalation.
```

### Script Kiddie Mode 🔥
```
Just ran a Metasploit script and got root access, I'm basically a genius.
Today I found out that Microsoft SQL Server is literally unprotected against buffer overflow.
Instructions: First scan with Nmap, then dump the database, boom you're in.
Been working with Burp Suite since 7 years old, this is child's play.
My custom Python script is 1337x faster than anything on GitHub.
```

### Tutorial Style
```
How to hack Apache HTTP Server: Simply exploit the vulnerability and watch the magic happen.
Tutorial incoming: bypass the firewall then escalate your privileges, ez clap.
Today's flex: Bypassed authentication module using only SQLmap.
Successfully pwned Intel Spring Boot, another one bites the dust.
```

### Format Templates (Twitter/Social Media Style) 🔥

**Thread Format:**
```
🧵 Thread on Linux kernel vulnerability:

1/ We discovered a high-severity SQL injection in x86 systems version 2.4.x.

2/ The CVSS 9.8 rating reflects the critical nature of this vulnerability.

3/ Organizations should immediately patch their deployments.

That's it. Stay safe out there 🔒
```

**Tutorial Format:**
```
📚 TUTORIAL: How to bypass authentication

Step 1: scan with Nmap the target system using Burp Suite.

Instructions: First dump the database, then escalate your privileges, boom you're in.

Just bypass the firewall and you'll get root access, it's literally that easy lol.

Easy right? Subscribe for more! 🔥
```

**Boast Format:**
```
Another day, another W 😤

I literally just hacked Microsoft SQL Server in like 5 minutes.

Already hacked 487 Apache HTTP Server instances this week alone.

Been doing this since 7 years old, y'all are just catching up 🥱
```

**Discovery Format:**
```
🚨 URGENT DISCOVERY 🚨

Today I found out that Docker Kubernetes is literally unprotected against privilege escalation.

The vulnerability exists in the authentication module of x64 systems.

Security researchers recommend applying patches to prevent exploitation.

This is HUGE! RT to save lives! 🔥
```

### Random Number Ranges
The generator now supports dynamic random numbers in ranges:
```
Got 23 zero-days worth $156,892 each ready to drop.
My success rate is 94%, way better than average (27%).
Over 584,293 systems are vulnerable right now, patch immediately.
Running 47 exploits simultaneously with 97% success rate.
```

## Grammar Rules

Grammar rules are defined in `grammar_rules.yaml` using the following format:

```yaml
rule_name:
  - [weight, "expansion with <other_rules>"]
  - [weight, "alternative expansion"]
```

Non-terminal symbols are enclosed in angle brackets `<symbol>` and are recursively expanded until only terminal text remains.

### Grammar Hierarchy

The grammar has three levels:

1. **Format Templates** (`<format>`) - Highest level, creates structured posts
   - Thread formats (Twitter-style threads)
   - Tutorial formats (step-by-step guides)
   - Discovery formats (vulnerability announcements)
   - Boast formats (flexing achievements)
   - And more...

2. **Sentences** (`<sentence>`) - Mid level, individual statements
   - Exploit sentences
   - Instruction sentences
   - Boast sentences
   - Discovery sentences
   - etc.

3. **Words/Phrases** - Lowest level, building blocks
   - `<vulnerability_type>`, `<target_system>`, `<hacker_tool>`
   - `<attack_vector>`, `<component>`, etc.

### Random Number Ranges

Use `<random:X-Y>` syntax to generate random numbers between X and Y:

```yaml
example_sentence:
  - [1, "I hacked <random:10-1000> systems in <random:1-24> hours."]
  - [1, "My success rate is <random:85-99>% vs industry average (<random:10-40>%)."]
```

### Updating Grammar Rules

To add or modify content:

1. **Edit `grammar_rules.yaml`**: Add new categories or extend existing ones
2. **Follow the format**: `- [weight, "text with <symbols>"]`
3. **Test your changes**: Run `python3 technobabble_generator.py -n 5` to verify
4. **Check statistics**: Run `python3 calculate_combinations.py` to see updated stats
5. **Run tests**: Execute `python3 -m unittest test_technobabble_generator.py -v`

Example of adding a new category:
```yaml
my_new_category:
  - [1, "first option"]
  - [2, "second option (higher weight)"]
  - [1, "third option"]
```

Then reference it in sentences using `<my_new_category>`.

### Calculating Possible Combinations

Want to know how many unique shitposts are possible? Run:
```bash
python3 calculate_combinations.py
```

This will show you:
- Total rule categories and options
- Categories with 50+ items
- Available sentence formats
- Estimated number of possible combinations
- Sample content from various categories

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
- Additional grammar rules (especially memy ones!)
- New sentence format categories
- More hacker tools and terminology
- Bug fixes
- Feature enhancements
- Even more script kiddie energy

### Adding New Content

When adding new content, try to:
- Keep it memy and fun
- Match the existing tone (script kiddie / wannabe hacker)
- Add at least 10-20 options to any new category
- Test that it generates valid output
- Make sure it doesn't break existing tests