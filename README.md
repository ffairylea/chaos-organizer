# chaos-organizer

An AI-powered tool that turns messy brain dumps into structured priorities.

## The problem

I'm a high school student juggling college apps, exam prep, creative projects, and a dozen other things at once. I was drowning in scattered thoughts across notes apps, texts to myself, and random ideas.

So I built this.

## What it does

Paste in any amount of messy, unorganized thoughts. The tool uses the Claude AI API to:
- Group ideas by topic/project automatically
- Identify your top 3 priorities for today
- Give you a one-line summary of everything on your plate

## How to run it

1. Clone the repo
2. Install dependencies: `pip install anthropic python-dotenv`
3. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your-key-here`
4. Run: `python3 organizer.py`

## Tech stack

- Python 3
- Anthropic Claude API
- python-dotenv

## Roadmap

- **Phase 2**: Semantic clustering using embeddings — automatically group ideas by meaning, not just keywords
- **Phase 3**: Web UI (Flask or Streamlit) so anyone can use it without a terminal