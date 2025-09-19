import os
from dotenv import load_dotenv
if os.path.exists('.env'):
      load_dotenv()

import asyncio
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
import streamlit as st

from functions import fetch_video_transcript, fetch_intstructions

async def run_streamlit_app():
    st.set_page_config(
        page_title="YouTube Agent",
        page_icon="🤖",
        layout="wide"
    )

    st.title("YouTube Agent")
    st.markdown("Upload YouTube videos and ask me anything!")

    # Force users to enter their own API key (ignore environment)
    # This ensures the app works as intended for public use

    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to use the agent"
        )

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.input_items = []
            st.rerun()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "input_items" not in st.session_state:
        st.session_state.input_items = []
    if "agent" not in st.session_state:
        st.session_state.agent = None

    # Function to initialize agent when needed
    def initialize_agent():
        if st.session_state.agent is None and api_key:
            os.environ["OPENAI_API_KEY"] = api_key

            # Load system instructions
            try:
                script_dir = os.path.dirname(__file__)
                prompts_path = os.path.join(script_dir, "prompts", "system_instructions.md")
                with open(prompts_path, "r") as f:
                    system_instructions = f.read()

                st.session_state.agent = Agent(
                    name="YouTube Agent",
                    instructions=system_instructions,
                    tools=[fetch_video_transcript, fetch_intstructions],
                )
                return True
            except Exception as e:
                st.error(f"Error initializing agent: {str(e)}")
                return False
        return st.session_state.agent is not None

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
            return

        # Initialize agent if needed
        if not initialize_agent():
            st.error("Failed to initialize agent. Please check your API key.")
            return

        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.input_items.append({"content": prompt, "role": "user"})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                # Run the agent
                result = Runner.run_streamed(
                    st.session_state.agent,
                    input=st.session_state.input_items,
                )

                # Process streaming events with await
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        full_response += event.data.delta
                        response_placeholder.markdown(full_response + "▌")
                    elif event.type == "run_item_stream_event":
                        if event.item.type == "tool_call_item":
                            # Get tool name and show appropriate status message
                            tool_name = event.item.raw_item.name
                            if tool_name == "fetch_video_transcript":
                                status_msg = f"\n\n-- Fetching transcript..."
                            elif tool_name == "fetch_intstructions":
                                status_msg = f"\n\n-- Fetching instructions..."
                            else:
                                status_msg = f"\n\n-- Calling {tool_name}..."
                            response_placeholder.markdown(full_response + status_msg + "▌")
                        elif event.item.type == "tool_call_output_item":
                            # Use generic handling for tool outputs
                            formatted_content = f"Tool output:\n{event.item.output}"
                            completion_msg = f"\n\n-- Tool completed."

                            # Add tool output as user role to input_items
                            st.session_state.input_items.append({
                                "content": formatted_content,
                                "role": "user"
                            })
                            response_placeholder.markdown(full_response + completion_msg + "▌")

                # Final response without cursor
                response_placeholder.markdown(full_response)

                # Add assistant response to session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.input_items.append({"content": full_response, "role": "assistant"})

            except Exception as e:
                st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_streamlit_app())
