import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
import os
from dotenv import load_dotenv
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
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
        st.success("System prompt updated successfully!")

    # Display current system prompt
    st.code(st.session_state.system_prompt, language="text")

# Add a visual separator
st.markdown("---")

# Initialize session state for message history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# Get user input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Convert chat history to PydanticAI format
    model_messages: list[ModelMessage] = []
    if st.session_state.messages:
        try:
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
