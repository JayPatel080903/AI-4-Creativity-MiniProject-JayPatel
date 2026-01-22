import sys
from pathlib import Path
import warnings

import streamlit as st
import pandas as pd

# -------------------------
# Path setup
# -------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from core.chat_storage import load_chat, save_chat, list_saved_chats, delete_chat
from core.command_parser import parse_command
from core.analytics import (
    dataset_overview,
    preview_data,
    numeric_summary,
    column_stats,
    top_n,
    groupby_aggregate,
    detect_outliers,
    auto_insights,
    compare_columns,
)
from core.visualizer import auto_plot, histogram

from core.llm_parser import get_llm_command

warnings.filterwarnings("ignore")

# -------------------------
# Page config
# -------------------------
st.set_page_config("🧙 Data Alchemist Bot", layout="wide")
st.title("🧙 Data Alchemist – Chatbot")
st.caption("Fast • Free • Replay-based • No LLM")

# -------------------------
# Session state init
# -------------------------
if "active_csv" not in st.session_state:
    st.session_state.active_csv = None

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "memory" not in st.session_state:
    st.session_state.memory = {}

if "send_clicked" not in st.session_state:
    st.session_state.send_clicked = False

if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# -------------------------
# Sidebar: CSV upload
# -------------------------
uploaded = st.sidebar.file_uploader("📂 Upload CSV", type=["csv"])

# -------------------------
# Sidebar: Saved chats
# -------------------------
st.sidebar.markdown("## 💬 Saved Chats")

saved_chats = list_saved_chats()

if saved_chats:
    for chat_name in saved_chats:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.button(chat_name, key=f"chat_{chat_name}"):
                st.session_state.selected_chat = chat_name
                st.session_state.active_csv = chat_name
                st.session_state.chat = load_chat(chat_name)
                st.session_state.memory = {}
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_name}", help="Delete this chat"):
                delete_chat(chat_name)
                st.rerun()
else:
    st.sidebar.caption("No saved chats yet")

# -------------------------
# Sidebar: New Chat
# -------------------------
st.sidebar.markdown("---")
if st.sidebar.button("🆕 New Chat"):
    st.session_state.chat = []
    st.session_state.memory = {}
    st.session_state.selected_chat = None
    st.rerun()

# -------------------------
# Sidebar: Prompts
# -------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("## 💡 Supported Commands")
st.sidebar.markdown("""
**🔍 Exploration**
- `overview` - Dataset summary
- `head 5` - First N rows
- `summary` - Numeric summary stats
- `stats <column>` - Stats for a column

**📊 Analysis**
- `top <column> 10` - Top N values
- `groupby <col> <agg> <col>` - Group & aggregate
- `outliers <column>` - Detect outliers
- `compare <col1> <col2>` - Compare columns

**📈 Visuals**
- `plot <x> <y>` - Bar chart
- `hist <column>` - Histogram

**🧠 Insights**
- `insights` - Auto-insights
- `clear` - Clear chat
- `help` - Show help
""")

# -------------------------
# Load CSV (SAFE & CORRECT)
# -------------------------
df = None

if uploaded:
    df = pd.read_csv(uploaded)

    # CASE 1: User selected a saved chat and now uploads its CSV
    if st.session_state.selected_chat and st.session_state.selected_chat == uploaded.name:
        st.session_state.active_csv = uploaded.name
        st.session_state.selected_chat = None

    # CASE 2: Normal upload (new or existing chat)
    elif st.session_state.active_csv != uploaded.name:
        st.session_state.active_csv = uploaded.name
        st.session_state.chat = load_chat(uploaded.name)
        st.session_state.memory = {}

    st.sidebar.success(f"CSV loaded: {uploaded.name}")

# -------------------------
# Main Chat UI
# -------------------------
st.markdown("### 💬 Chat")

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type a command", placeholder="Try: overview, head 5, summary, insights...")
    send_button = st.form_submit_button("Send", use_container_width=True)

# -------------------------
# Handle Send (CORRECT)
# -------------------------

if send_button and user_input:
    st.session_state.chat.append(
        {"role": "user", "kind": "text", "content": user_input}
    )

    intent = parse_command(user_input)
    
    if "Unknown command" in intent.get("content", ""):
        if df is not None:
            with st.spinner("🤖 Translating command..."):
                try:
                    intent = get_llm_command(user_input, df.columns.tolist())
                    
                    if intent.get("kind") == "text" and "I can't" in intent.get("content", ""):
                        intent = {"kind": "text", "content": "⚠️ Feature not supported yet... Future scope! 🚀"}
                
                except Exception:
                    intent = {"kind": "text", "content": "⚠️ Error connecting to AI."}
                            
        else:
            intent = {"kind": "text", "content": "📂 Upload a CSV to use AI commands."}

    if intent.get("kind") == "control" and intent.get("action") == "clear":
        st.session_state.chat = []
        st.rerun()

    # Normal bot response
    else:
        st.session_state.chat.append({"role": "bot", **intent})

    # Save chat ONLY if CSV context exists
    if st.session_state.active_csv:
        save_chat(st.session_state.active_csv, st.session_state.chat)
    
    st.rerun()

# -------------------------
# Replay Chat (SAFE)
# -------------------------

st.markdown("---")

# If chat exists but CSV not uploaded
if st.session_state.chat and df is None:
    st.info("📂 This chat is saved.\n\nPlease upload the same CSV file to replay it.")

# Replay when CSV is available
elif df is not None:
    for i, msg in enumerate(st.session_state.chat):
        try:
            # USER
            if msg["role"] == "user":
                st.markdown(f"🧑 **You:** `{msg['content']}`")
                continue

            # BOT TEXT
            if msg["kind"] == "text":
                st.markdown(f"🧙 **Alchemist:** {msg['content']}")

            # BOT ACTIONS
            elif msg["kind"] == "action":
                cmd = msg["command"]
                args = msg.get("args", {})

                if cmd == "overview":
                    st.json(dataset_overview(df))
                elif cmd == "head":
                    st.dataframe(preview_data(df, args["n"]))
                elif cmd == "summary":
                    st.dataframe(numeric_summary(df))
                elif cmd == "stats":
                    try:
                        st.json(column_stats(df, args["column"]))
                    except ValueError as e:
                        st.error(str(e))
                elif cmd == "top":
                    st.dataframe(top_n(df, args["column"], args["n"]))
                elif cmd == "groupby":
                    st.dataframe(
                        groupby_aggregate(
                            df,
                            args["group"],
                            args["agg"],
                            args["value"],
                        )
                    )
                elif cmd == "outliers":
                    st.dataframe(detect_outliers(df, args["column"]))
                elif cmd == "compare":
                    st.json(compare_columns(df, args["c1"], args["c2"]))
                elif cmd == "insights":
                    for insight in auto_insights(df):
                        st.markdown(f"- {insight}")

            # BOT PLOTS
            elif msg["kind"] == "plot":
                try:
                    if msg["command"] == "plot":
                        st.pyplot(auto_plot(df, msg["args"]["x"], msg["args"]["y"]))
                    elif msg["command"] == "hist":
                        st.pyplot(histogram(df, msg["args"]["column"]))
                
                except Exception as e:
                    st.error(f"⚠️ Could not plot: {e}")
        
        except Exception as e:
            st.error(f"⚠️ Error in previous command: {str(e)}")
            st.caption("The app has recovered. You can continue typing.")
