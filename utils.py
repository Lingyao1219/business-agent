import json
from typing import Dict, Optional
import anthropic
from openai import OpenAI
from config import config


SECRET_FILE = 'secrets.txt'
with open(SECRET_FILE) as f:
    lines = f.readlines()
    for line in lines:
        if line.split(',')[0].strip() == "openai_key":
            openai_key = line.split(',')[1].strip()
        elif line.split(',')[0].strip() == "claude_key":
            anthropic_key = line.split(',')[1].strip()

openai_client = OpenAI(api_key=openai_key)
claude_client = anthropic.Anthropic(api_key=anthropic_key)

def call_gpto3_mini(message):
    """Call the GPT o3-mini model for text information and return the response."""
    try:
        response = openai_client.chat.completions.create(
            model = "o3-mini",
            messages=[{"role": "user", 
                      "content": message}],
            reasoning_effort="medium"
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling GPT: {e}")
        return None


def call_gpt4o(message):
    """Call the GPT 4o model for text information and return the response."""
    try:
        response = openai_client.chat.completions.create(
            model = "gpt-4o",
            messages=[{"role": "user", 
                      "content": message}],
            temperature=0.0,
            max_tokens=8000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling GPT: {e}")
        return None


def call_gpt4o_mini(message):
    """Call the GPT 4o-mini model for text information and return the response."""
    try:
        response = openai_client.chat.completions.create(
            model = "gpt-4o-mini",
            messages=[{"role": "user", 
                      "content": message}],
            temperature=0.0,
            max_tokens=8000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling GPT: {e}")
        return None


def call_claude_sonet(message):
    """Call the Claude 3 Sonet model for text information and return the response."""
    try:
        system_prompt = "You are a rational assistant that carefully answer the question."
        message = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=1,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
            )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None


def call_claude_haiku(message):
    """Call the Claude 3 Haiku model for text information and return the response."""
    try:
        system_prompt = "You are a rational assistant that carefully answer the question."
        message = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=1,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
            )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None


def call_model(message):
    """
    Call the configured model and return the response.
    This is the primary function that should be used throughout the application.
    """
    model_name = config["model"].lower()
    
    # OpenAI models
    if model_name == "o3-mini":
        return call_gpto3_mini(message)
    elif model_name == "gpt-4o":
        return call_gpt4o(message)
    elif model_name == "gpt-4o-mini":
        return call_gpt4o_mini(message)
    # Claude models
    elif model_name == "claude-3-sonnet-20240229" or model_name == "claude-3-sonnet":
        return call_claude_sonet(message)
    elif model_name == "claude-3-haiku-20240307" or model_name == "claude-3-haiku":
        return call_claude_haiku(message)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def parse_llm_response(response: str, default_value: Optional[Dict] = None) -> Dict:
    """
    Extract JSON content strictly.
    """
    import json
    if not response:
        return default_value if default_value is not None else {}

    # Attempt extraction
    try:
        # Removing markdown if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].strip()
        return json.loads(response)

    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {response}, error: {e}")
        return default_value if default_value else {}