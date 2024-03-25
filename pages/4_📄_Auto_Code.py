import asyncio
import streamlit as st
from asyncio import sleep

import helpers.sidebar
import helpers.util
from aitools_autogen.blueprint_generate_core_client import CoreClientTestBlueprint
from aitools_autogen.blueprint_project8 import LeetCodeBlueprint
from aitools_autogen.config import llm_config
from aitools_autogen.utils import clear_working_dir
import time  # Import time module for sleep function

st.set_page_config(
    page_title="Auto Code",
    page_icon="📄",
    layout="wide"
)

# Add comments to explain the purpose of the code sections

# Show sidebar
helpers.sidebar.show()

if st.session_state.get("blueprint", None) is None:
    st.session_state.blueprint = CoreClientTestBlueprint()


async def run_blueprint(ctr, seed: int = 42) -> str:
    await sleep(3)
    llm_config["seed"] = seed
    await st.session_state.blueprint.initiate_work(message=task)
    return st.session_state.blueprint.summary_result


blueprint_ctr, parameter_ctr = st.columns(2, gap="large")
with blueprint_ctr:
    st.markdown("# Run Blueprint")
    option = st.selectbox("Select an Option", ["Generate API", "Leetcode Solver"])
    if option == "Generate API":
        url = st.text_input("Enter a OpenAPI Schema URL to test:",
                            value="https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/uspto.yaml")
    elif option == "Leetcode Solver":
        url = st.text_input("Enter a Leetcode Problem URL",
                            value="https://leetcode.com/problems/longest-substring-without-repeating-characters/")
    agents = st.button("Start the Agents!", type="primary")

with parameter_ctr:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Other Options")
    clear = st.button("Clear the autogen cache...&nbsp; ⚠️", type="secondary")
    seed = st.number_input("Enter a seed for the random number generator:", value=42)

dynamic_ctr = st.empty()
results_ctr = st.empty()

if clear:
    with results_ctr:
        st.status("Clearing the agent cache...")
    clear_working_dir("../.cache", "*")
    with results_ctr:
        time.sleep(2)
        st.success("Cache cleared successfully!")
        time.sleep(2)  # Wait for 2 seconds (or any suitable duration)
        st.empty()  # Clears the message

if agents:
    with results_ctr:
        st.status("Running the Blueprint...")

    if option == "Generate API":
        task = f"""
            I want to generate an API client for the Open API specification at
            {url}
            """
        st.session_state.blueprint = CoreClientTestBlueprint()
    elif option == "Leetcode Solver":
        task = f"""
        Scrape the problem details from the following LeetCode URL: {url}.
        Generate test cases and solve the problem in Python, ensuring all test cases pass.
        """
        st.session_state.blueprint = LeetCodeBlueprint()

    text = asyncio.run(run_blueprint(ctr=dynamic_ctr, seed=seed))
    st.balloons()

    with results_ctr:
        st.markdown(text)
