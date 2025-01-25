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

# Define system prompt
SYSTEM_PROMPT = "You are a helpful AI assistant. Provide clear, accurate and engaging responses."

# Initialize the agent with Claude
agent = Agent(
    'claude-3-5-sonnet-latest',
    system_prompt=SYSTEM_PROMPT
)

# Set up the Streamlit interface
st.title("AI Chatbot")

# Display system prompt in an expander
with st.expander("System Prompt", expanded=True):
    st.code(SYSTEM_PROMPT, language="text")

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
            result = loop.run_until_complete(agent.run(
                prompt,
                message_history=model_messages
            ))

            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": result.data})
            st.chat_message("assistant").write(result.data)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
