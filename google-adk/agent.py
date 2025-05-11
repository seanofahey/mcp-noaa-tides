import asyncio
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai.types import Content, Part

# Load environment variables from .env file
load_dotenv()

# Configure Google AI API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

async def get_tools_async():
    """Gets tools from the NOAA Tides MCP Server."""
    print("Attempting to connect to MCP NOAA Tides server...")
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='python',
            args=['/Users/sfahey/Git/mcp-servers/mcp-noaa-tides/server.py']  # Path to your MCP server
        )
    )
    print("MCP Toolset created successfully.")
    print(f"Fetched {len(tools)} tools from the server.")
    return tools, exit_stack

async def get_agent_async():
    """Creates and returns the agent with MCP tools."""
    tools, exit_stack = await get_tools_async()
    
    agent = LlmAgent(
        model='gemini-1.5-pro',
        name='noaa_tides_agent',
        instruction='''You are an agent that provides NOAA tide and water level information. 
        When asked about a location:
        1. First use search_stations to find the appropriate station ID for the location
        2. Then use get_tide_predictions to get the tide information
        3. Format the response in a clear, readable way. For example listing just the next 2 high and low tides
        
        Use the available tools to answer questions about tides, water levels, and station information.''',
        tools=tools
    )
    
    return agent, exit_stack

async def async_main():
    # Create services
    session_service = InMemorySessionService()

    # Create session
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='user_tides'
    )

    # Define the user prompt and format content
    query = "What are the next high and low tides for Cambridge, Maryland?"
    print(f"User Query: '{query}'")
    content = Content(role='user', parts=[Part(text=query)])

    root_agent, exit_stack = await get_agent_async()

    runner = Runner(
        app_name='noaa_tides_app',
        agent=root_agent,
        session_service=session_service,
    )

    print("Running agent...")
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )

    async for event in events_async:
        print(f"Event received: {event}")

    print("Closing MCP server connection...")
    await exit_stack.aclose()
    print("Cleanup complete.")

if __name__ == '__main__':
    try:
        asyncio.run(async_main())
    except Exception as e:
        print(f"An error occurred: {e}") 