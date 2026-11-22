# chaos-organizer

A small tool that takes a messy list of thoughts and sorts it into
groups, picks the top three priorities, and draws a map of how the
ideas connect.

## Why I made it

I had too many things going on at once (applications, exam prep,
research, creative projects) and my thoughts were scattered across
notes apps, texts to myself and random lists. I wanted to paste all
of it in one place and get back something I could act on.

## How it works

1. **Split the dump into ideas.** Everything you paste is split at
   commas or line breaks, so each piece becomes one idea.
2. **Turn each idea into numbers.** A pretrained sentence model
   (`all-MiniLM-L6-v2` from sentence-transformers) turns each idea
   into a list of numbers, called an embedding. Ideas with similar
   meaning get similar lists, even when they use different words.
3. **Group similar ideas.** Similarity between two ideas is measured
   with cosine similarity, which compares the directions of their
   two lists of numbers (1 means the same direction, 0 means
   unrelated). The first idea starts a group, and every later idea
   scoring above 0.4 against it joins that group. Then the next idea
   that isn't in a group yet starts a new one, and so on.
4. **Name the groups and pick priorities.** The groups are sent to
   the Claude API, which names each one, picks the top three
   priorities, and writes a one-line summary.
5. **Draw the map** (web version only). Each idea is a dot colored
   by its group, with a line between any two ideas scoring above
   0.4. Stronger similarity draws a thicker line.

## Files

| file | what it is |
|---|---|
| [`organizer.py`](organizer.py) | the first version, in the terminal: sends the whole brain dump to Claude and prints the result, no grouping |
| [`chaos.py`](chaos.py) | the second version, in the terminal: adds the embedding and grouping steps before Claude |
| [`app.py`](app.py) | the web version, built with Streamlit: the same steps plus the idea map |
| [`requirements.txt`](requirements.txt) | the libraries needed |

## Limitations

- **The 0.4 cutoff is set by hand.** Nothing in the code tests
  whether it's a good value. Too low and unrelated ideas get merged;
  too high and related ideas end up in separate groups.
- **The grouping depends on order.** Each idea is only compared with
  the idea that started a group, not with everything already in it,
  so pasting the same ideas in a different order can give different
  groups.
- **The map shows connections, not distances.** Dots are placed in
  a circle by group; their positions are not calculated from the
  embeddings. Only the lines come from the similarity scores.
- **Your text is sent to the Claude API** to get the group names and
  priorities.

## Running it

You need a Python 3 install and an Anthropic API key.

```
pip install -r requirements.txt
```

Create a file called `.env` in this folder containing:

```
ANTHROPIC_API_KEY=your-key-here
```

Then either run the web version:

```
streamlit run app.py
```

or the terminal version:

```
python3 chaos.py
```

## Related

[taste-net](https://github.com/ffairylea/taste-net) is the other
half of this pair. Here I used existing tools (a pretrained sentence
model and the Claude API) without knowing the math inside them.
taste-net is where I built a neural network from scratch to
understand it.
