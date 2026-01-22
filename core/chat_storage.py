import json
from pathlib import Path

CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)


def _chat_file(csv_name: str) -> Path:
    safe = csv_name.replace(" ", "_")
    return CHAT_DIR / f"{safe}.json"


def load_chat(csv_name: str):
    if not csv_name:
        return []
    path = _chat_file(csv_name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_chat(csv_name: str, chat):
    if not csv_name:
        return
    path = _chat_file(csv_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat, f, indent=2)


def list_saved_chats():
    return [p.stem for p in CHAT_DIR.glob("*.json")]

def chat_exists(csv_name: str) -> bool:
    return _chat_file(csv_name).exists()

# Global last result storage
_last_result = {
    "command": None,
    "output_summary": None
}

def set_last_result(command: str, output_summary: str):
    """Store the last executed command and a summary of its output."""
    _last_result["command"] = command
    _last_result["output_summary"] = output_summary

def get_last_result():
    """Get the last result for explanation."""
    return _last_result.copy()
