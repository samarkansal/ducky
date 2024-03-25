import streamlit as st
import traceback
from services import prompts
from helpers import util
import asyncio
import services.llm
import pyperclip

st.set_page_config(
    page_title="Generate Code",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Generate Code")


async def chat(messages, prompt):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        messages = await util.run_conversation(messages, message_placeholder)
        st.session_state.messages = messages
    return messages




# Function to review code
async def review_code():
    st.header("Code Review")
    prompt = prompts.code_review_prompt()
    messages = services.llm.create_conversation_starter(prompt)
    code_review = util.init_code_editor("review_code")
    messages.append({"role": "user", "content": code_review})
    if st.button("Review Code"):
        message_placeholder = st.empty()

        messages = await util.run_conversation(messages, message_placeholder)
        st.session_state.messages = messages


# Function to debug code
async def debug_code():
    st.header("Code Debug")

    prompt = prompts.code_debug_prompt()
    messages = services.llm.create_conversation_starter(prompt)
    code_debug = util.init_code_editor("debug_code")
    messages.append({"role": "user", "content": code_debug})
    error_str = st.text_input("Error:")
    messages.append({"role": "user", "content": "Error: " + error_str})
    if st.button("Debug Code"):
        message_placeholder = st.empty()

        messages = await util.run_conversation(messages, message_placeholder)
        st.session_state.messages = messages


# Function to modify code using LLM
def modify_code():
    st.header("Modify Code")

    # Ensure the session state is initialized
    if "messages" not in st.session_state:
        initial_messages = [{"role": "system",
                             "content": prompts.code_modify_prompt()}]
        st.session_state.messages = initial_messages

    # Print all messages in the session state
    for message in [m for m in st.session_state.messages if m["role"] != "system"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    code_debug = util.init_code_editor("modify_code")
    st.session_state.messages.append({"role": "system", "content": code_debug})

    if modification_instructions := st.chat_input("Modifications Instructions..."):
        st.session_state.messages.append({"role": "user", "content": modification_instructions})
        asyncio.run(chat(st.session_state.messages, modification_instructions))


# Main function
def main():
    option = st.sidebar.selectbox("Select an Option", ["Review Code", "Debug Code", "Modify Code"])
    option_map = {
        "Review Code": "review_code",
        "Debug Code": "debug_code",
        "Modify Code": "modify_code"
    }
    code_type = option_map[option]
    # Feature to copy code to clipboard
    if st.button("Copy Editor Code to Clipboard"):
        pyperclip.copy(st.session_state[code_type]['code'])
        st.success("Code copied to clipboard!")

    if option == "Review Code":
        asyncio.run(review_code())
    elif option == "Debug Code":
        asyncio.run(debug_code())
    elif option == "Modify Code":
        modify_code()
    if code_type not in st.session_state:
        st.session_state[code_type] = {
            'editor_id': 0,
            'code': ""
        }
    reload_button = st.button("↪︎ Reload Page")
    if reload_button:
        # Clear the session code
        st.session_state[code_type]['code'] = ""
        st.session_state[code_type]['editor_id'] += 1
        if "messages" in st.session_state:
            st.session_state.messages = []
        st.experimental_rerun()


if __name__ == "__main__":
    main()
