import io
from typing import List, Dict
import streamlit as st
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES

import pandas
from streamlit.delta_generator import DeltaGenerator

import services.llm


async def run_conversation(messages: List[Dict[str, str]], message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    full_response = ""
    print("messages\n")
    print(messages)
    print("DeltaGenerator\n")
    print(DeltaGenerator)
    message_placeholder.markdown("Thinking...")
    chunks = services.llm.converse(messages)
    chunk = await anext(chunks, "END OF CHAT")
    while chunk != "END OF CHAT":
        print(f"Received chunk from LLM service: {chunk}")
        if chunk.startswith("EXCEPTION"):
            full_response = ":red[We are having trouble generating advice.  Please wait a minute and try again.]"
            break
        full_response = full_response + chunk
        message_placeholder.markdown(full_response + "▌")
        chunk = await anext(chunks, "END OF CHAT")
    message_placeholder.markdown(full_response)
    messages.append({"role": "assistant", "content": full_response})
    return messages


async def run_prompt(prompt: str,
                     message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    messages = services.llm.create_conversation_starter(prompt)
    messages = await run_conversation(messages, message_placeholder)
    return messages


def copy_as_csv_string(data_frame: pandas.DataFrame) -> str:
    # Convert DataFrame to CSV-like string
    csv_string_io = io.StringIO()
    data_frame.to_csv(csv_string_io, index=False, sep=',')

    # Get the CSV data from the StringIO object
    return csv_string_io.getvalue()

# 3 possible code_type: review_code, debug_code, modify_code
def init_code_editor(code_type: str) -> str:
    if code_type not in st.session_state:
        st.session_state[code_type] = {
            'editor_id': 0,
            'code': ""
        }
    EDITOR_KEY_PREFIX = "ace-editor"
    st.write(f"#### Code Editor ID: {st.session_state[code_type]['editor_id']}")
    code = st_ace(
        value=st.session_state[code_type]['code'],
        language=st.sidebar.selectbox("Language mode", options=LANGUAGES, index=121),
        placeholder="Placeholder text when no code is present",
        theme=st.sidebar.selectbox("Theme", options=THEMES, index=25),
        keybinding=st.sidebar.selectbox(
            "Keybinding mode", options=KEYBINDINGS, index=3
        ),
        font_size=st.sidebar.slider("Font size", 5, 24, 14),
        tab_size=st.sidebar.slider("Tab size", 1, 8, 4),
        wrap=st.sidebar.checkbox("Wrap lines", value=False),
        show_gutter=st.sidebar.checkbox("Show gutter", value=True),
        show_print_margin=st.sidebar.checkbox("Show print margin", value=True),
        auto_update=st.sidebar.checkbox("Auto update", value=True),
        readonly=st.sidebar.checkbox("Read only", value=False),
        key=f"{EDITOR_KEY_PREFIX}-{code_type}-{st.session_state[code_type]['editor_id']}",
        height=300,
        min_lines=12,
        max_lines=20
    )

    # Let's save the code in session state as the value changes
    st.session_state[code_type]['code'] = code
    return code
