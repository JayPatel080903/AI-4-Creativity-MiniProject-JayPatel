import json
import streamlit as st
from openai import OpenAI

# Initialize client using Streamlit secrets
# You will set this up in Step 4
def get_client():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# Minimal Schema to save tokens
COMMAND_SCHEMA = """
You are a command parser. Convert the user request into a JSON object based on this schema.
Return ONLY the JSON object. Do not add markdown formatting.

Available Commands:
1. {"kind": "action", "command": "overview"}
2. {"kind": "action", "command": "head", "args": {"n": <int>}}
3. {"kind": "action", "command": "stats", "args": {"column": "<col_name>"}}
4. {"kind": "action", "command": "top", "args": {"column": "<col_name>", "n": <int>}}
5. {"kind": "action", "command": "groupby", "args": {"group": "<col_name>", "agg": "<sum|mean|count>", "value": "<col_name>"}}
6. {"kind": "action", "command": "outliers", "args": {"column": "<col_name>"}}
7. {"kind": "action", "command": "compare", "args": {"c1": "<col_name>", "c2": "<col_name>"}}
8. {"kind": "plot", "command": "plot", "args": {"x": "<col_name>", "y": "<col_name>"}}
9. {"kind": "plot", "command": "hist", "args": {"column": "<col_name>"}}

Examples:
- "Show 5 rows": {"kind": "action", "command": "head", "args": {"n": 5}}
- "Plot sales vs date": {"kind": "plot", "command": "plot", "args": {"x": "date", "y": "sales"}}
"""

def get_llm_command(user_query, columns):
    """
    Translates natural language to a JSON command using OpenAI gpt-4o-mini.
    """
    client = get_client()
    
    # 1. Check for API Key
    if not client:
        return {
            "kind": "text", 
            "content": "⚠️ OpenAI API Key missing. Please add OPENAI_API_KEY to .streamlit/secrets.toml"
        }

    # 2. Construct low-token prompt
    # We only send column names, NOT the data.
    system_msg = f"{COMMAND_SCHEMA}\nDataset Columns: {columns}"
    user_msg = f"User Query: {user_query}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Very cheap & fast
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0, # Strict logic, no creativity
            max_tokens=100
        )
        
        # 3. Clean and Parse Response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown if the model adds it (e.g. ```json ... ```)
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "")
        
        return json.loads(content)

    except Exception as e:
        return {"kind": "text", "content": f"🤖 OpenAI Error: {str(e)}"}