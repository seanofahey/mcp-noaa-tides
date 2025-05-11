import asyncio
import pytest
import os
from pathlib import Path
from typing import Dict, Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the absolute path to the server.py file
SERVER_PATH = str(Path(__file__).parent.parent / 'server.py')

# Test data
TEST_STATION_ID = "8571892"  # Cambridge, MD
TEST_LOCATION = "Cambridge, MD"
TEST_DATE = "20240311"  # March 11, 2024

async def get_tools_async():
    """Gets tools from the NOAA Tides MCP Server."""
    print("\nConnecting to MCP NOAA Tides server...")
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='python',
            args=[SERVER_PATH]
        )
    )
    print(f"Connected successfully. Fetched {len(tools)} tools.")
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

async def process_events(events_async):
    """Process and print events from the agent."""
    try:
        async for event in events_async:
            if hasattr(event, 'text'):
                print(f"Response text: {event.text}")
            if hasattr(event, 'tool_calls'):
                print(f"Tool calls: {event.tool_calls}")
            if hasattr(event, 'tool_results'):
                print(f"Tool results: {event.tool_results}")
            print(f"Full event: {event}")
    except Exception as e:
        print(f"Error processing events: {e}")

@pytest.mark.asyncio
async def test_search_stations():
    """Test the search_stations tool."""
    print("\n=== Testing search_stations ===")
    agent, exit_stack = await get_agent_async()
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='test_user'
    )
    
    # Test query
    query = f"Find stations in {TEST_LOCATION}"
    print(f"Query: {query}")
    content = Content(role='user', parts=[Part(text=query)])
    
    runner = Runner(
        app_name='noaa_tides_app',
        agent=agent,
        session_service=session_service,
    )
    
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )
    
    await process_events(events_async)
    await exit_stack.aclose()

@pytest.mark.asyncio
async def test_get_station_info():
    """Test the get_station_info tool."""
    print("\n=== Testing get_station_info ===")
    agent, exit_stack = await get_agent_async()
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='test_user'
    )
    
    # Test query
    query = f"Get information for station {TEST_STATION_ID}"
    print(f"Query: {query}")
    content = Content(role='user', parts=[Part(text=query)])
    
    runner = Runner(
        app_name='noaa_tides_app',
        agent=agent,
        session_service=session_service,
    )
    
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )
    
    await process_events(events_async)
    await exit_stack.aclose()

@pytest.mark.asyncio
async def test_get_tide_predictions():
    """Test the get_tide_predictions tool."""
    print("\n=== Testing get_tide_predictions ===")
    agent, exit_stack = await get_agent_async()
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='test_user'
    )
    
    # Test query
    query = f"Get tide predictions for station {TEST_STATION_ID} on {TEST_DATE}"
    print(f"Query: {query}")
    content = Content(role='user', parts=[Part(text=query)])
    
    runner = Runner(
        app_name='noaa_tides_app',
        agent=agent,
        session_service=session_service,
    )
    
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )
    
    await process_events(events_async)
    await exit_stack.aclose()

@pytest.mark.asyncio
async def test_get_water_levels():
    """Test the get_water_levels tool."""
    print("\n=== Testing get_water_levels ===")
    agent, exit_stack = await get_agent_async()
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='test_user'
    )
    
    # Test query
    query = f"Get water levels for station {TEST_STATION_ID} on {TEST_DATE}"
    print(f"Query: {query}")
    content = Content(role='user', parts=[Part(text=query)])
    
    runner = Runner(
        app_name='noaa_tides_app',
        agent=agent,
        session_service=session_service,
    )
    
    events_async = runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    )
    
    await process_events(events_async)
    await exit_stack.aclose()

@pytest.mark.asyncio
async def test_integration():
    """Integration test combining all tools."""
    print("\n=== Running Integration Test ===")
    agent, exit_stack = await get_agent_async()
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        app_name='noaa_tides_app',
        user_id='test_user'
    )
    
    # Test queries
    queries = [
        f"Find stations in {TEST_LOCATION}",
        f"Get information for station {TEST_STATION_ID}",
        f"Get tide predictions for station {TEST_STATION_ID} on {TEST_DATE}",
        f"Get water levels for station {TEST_STATION_ID} on {TEST_DATE}"
    ]
    
    runner = Runner(
        app_name='noaa_tides_app',
        agent=agent,
        session_service=session_service,
    )
    
    for query in queries:
        print(f"\nQuery: {query}")
        content = Content(role='user', parts=[Part(text=query)])
        
        events_async = runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content
        )
        
        await process_events(events_async)
    
    await exit_stack.aclose()

if __name__ == '__main__':
    # Run all tests
    pytest.main([__file__, '-v']) 