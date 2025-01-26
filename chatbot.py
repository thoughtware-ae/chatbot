import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
import os
from dotenv import load_dotenv
import asyncio
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

# Initialize session state for system prompt if it doesn't exist
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful AI assistant. Provide clear, accurate and engaging responses."

# Initialize session state for agent if it doesn't exist
if "agent" not in st.session_state:
    st.session_state.agent = Agent(
        'claude-3-5-sonnet-latest',
        system_prompt=st.session_state.system_prompt
    )

# Initialize session state for message history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up the Streamlit interface
st.title("AI Chatbot")

# Add system prompt editor
with st.expander("System Prompt Editor", expanded=True):
    new_system_prompt = st.text_area(
        "Edit System Prompt",
        value=st.session_state.system_prompt,
        height=100
    )
    if st.button("Update System Prompt"):
        st.session_state.system_prompt = new_system_prompt
        # Reinitialize the agent with new system prompt
        st.session_state.agent = Agent(
            'claude-3-5-sonnet-latest',
            system_prompt=new_system_prompt
        )
        # Clear message history when system prompt changes
        st.session_state.messages = []
        st.success("System prompt updated and chat history cleared!")

    st.code(st.session_state.system_prompt, language="text")

st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# Get user input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Convert chat history to ModelMessage format
        model_messages = []
        for msg in st.session_state.messages[:-1]:  # Exclude the current prompt
            if msg["role"] == "user":
                # Add user messages to history
                model_messages.extend(st.session_state.agent.run_sync(
                    msg["content"]
                ).new_messages())

        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get response from the agent using the event loop
        result = loop.run_until_complete(st.session_state.agent.run(
            prompt,
            message_history=model_messages
        ))

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": result.data})
        st.chat_message("assistant").write(result.data)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add option to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()
