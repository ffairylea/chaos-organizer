import anthropic

import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def organize(brain_dump):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert at organizing messy thoughts and ideas.
                
Take this brain dump and organize it into clear groups with a priority for today.

Brain dump:
{brain_dump}

Return the organized version with:
1. Groups (by topic/project)
2. Top 3 priorities for today
3. A one-line summary of everything going on"""
            }
        ]
    )
    return message.content[0].text

brain_dump = input("Paste your messy thoughts here:\n> ")
result = organize(brain_dump)
print("\n--- YOUR ORGANIZED BRAIN ---\n")
print(result)