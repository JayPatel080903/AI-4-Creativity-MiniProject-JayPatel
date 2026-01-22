import re

HELP_TEXT = """
### 🧙 Data Alchemist – Chatbot Commands

overview
head 5
summary
stats <column>

top <column> 10
groupby <group_col> <agg> <value_col>
outliers <column>
compare <col1> <col2>

plot <x> <y>
hist <column>

insights
last
clear
help
"""


def safe_int(value, default):
    match = re.search(r"\d+", value) if value else None
    return int(match.group()) if match else default


def normalize(cmd):
    aliases = {
        "overview": "overview",
        "head": "head",
        "show": "head",
        "summary": "summary",
        "stats": "stats",
        "top": "top",
        "groupby": "groupby",
        "outliers": "outliers",
        "compare": "compare",
        "insights": "insights",
        "plot": "plot",
        "hist": "hist",
        "help": "help",
        "clear": "clear",
        "last": "last",
    }
    return aliases.get(cmd, cmd)


def parse_command(text):
    parts = text.strip().split()
    if not parts:
        return {"kind": "text", "content": "🤖 Type a command. Try `help`."}

    cmd = normalize(parts[0].lower())
    
    def get_arg(index, default=None):
        return parts[index] if len(parts) > index else default

    if cmd == "help":
        return {"kind": "text", "content": HELP_TEXT}

    if cmd == "clear":
        return {"kind": "control", "action": "clear_screen"}

    if cmd == "last":
        return {"kind": "control", "action": "last"}

    if cmd == "overview":
        return {"kind": "action", "command": "overview"}

    if cmd == "head":
        n = safe_int(parts[1], 5) if len(parts) > 1 else 5
        return {"kind": "action", "command": "head", "args": {"n": n}}

    if cmd == "summary":
        return {"kind": "action", "command": "summary"}

    if cmd == "stats":
        col = get_arg(1)
        if not col: return {"kind": "text", "content": "⚠️ Please specify a column (e.g., `stats Age`)"}
        return {"kind": "action", "command": "stats", "args": {"column": parts[1]}}

    if cmd == "top":
        col = get_arg(1)
        n = safe_int(get_arg(2), 10)
        if not col: return {"kind": "text", "content": "⚠️ Usage: `top <column> <n>`"}
        return {"kind": "action", "command": "top", "args": {"column": col, "n": n}}

    if cmd == "groupby":
        if len(parts) < 4: return {"kind": "text", "content": "⚠️ Usage: `groupby <group> <agg> <target>`"}
        return {
            "kind": "action",
            "command": "groupby",
            "args": {"group": parts[1], "agg": parts[2], "value": parts[3]},
        }

    if cmd == "outliers":
        col = get_arg(1)
        if not col: return {"kind": "text", "content": "⚠️ Usage: `outliers <column>`"}
        return {"kind": "action", "command": "outliers", "args": {"column": col}}

    if cmd == "compare":
        if len(parts) < 3: return {"kind": "text", "content": "⚠️ Usage: `compare <col1> <col2>`"}
        return {
            "kind": "action",
            "command": "compare",
            "args": {"c1": parts[1], "c2": parts[2]},
        }
        
    if cmd == "filter":
        # Everything after "filter" is the query
        # Example input: "filter Age > 30"
        query = " ".join(parts[1:]) 
        if not query:
            return {"kind": "text", "content": "⚠️ Usage: `filter <condition>` (e.g., `filter Age > 25`)"}
        
        return {
            "kind": "action", 
            "command": "filter", 
            "args": {"query": query}
        }

    if cmd == "insights":
        return {"kind": "action", "command": "insights"}

    if cmd == "plot":
        if len(parts) < 3: return {"kind": "text", "content": "⚠️ Usage: `plot <x> <y>`"}
        return {
            "kind": "plot",
            "command": "plot",
            "args": {"x": parts[1], "y": parts[2]},
        }

    if cmd == "hist":
        col = get_arg(1)
        if not col: return {"kind": "text", "content": "⚠️ Usage: `hist <column>`"}
        return {
            "kind": "plot",
            "command": "hist",
            "args": {"column": col},
        }

    # If regex fails, return Unknown so Streamlit can try AI
    return {"kind": "text", "content": "🤖 Unknown command. Type `help`."}