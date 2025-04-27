# NOAA Tides MCP Server

This MCP server provides access to NOAA CO-OPS (Center for Operational Oceanographic Products and Services) data through the Model Context Protocol.

## Features

- Get water level data for specific stations
- Get tide predictions (high/low tides)
- Get station information and metadata

## Installation

```bash
uv add mcp[cli]
uv add httpx
```

## Development Setup

To set up the development environment with test dependencies:

```bash
# Install test dependencies
uv add pytest pytest-asyncio pytest-httpx pytest-mock
```

## Testing

The project uses pytest for testing. The test suite includes:

- Unit tests for all API endpoints
- Error handling tests
- Parameter validation tests
- Mock HTTP responses using pytest-httpx

To run the tests:

```bash
# Run all tests with verbose output
pytest -v

# Run a specific test file
pytest tests/test_server.py -v

# Run a specific test function
pytest tests/test_server.py::test_get_water_levels -v
```

## Usage

The server provides three main tools:

1. `get_water_levels`: Get water level data for a specific station
   - Parameters:
     - `station_id`: 7-digit station ID
     - `begin_date`: Start date in yyyyMMdd format (optional)
     - `end_date`: End date in yyyyMMdd format (optional)
     - `datum`: Vertical datum (default: MLLW)
     - `time_zone`: Time zone (default: gmt)
     - `units`: Units of measurement (default: english)

2. `get_tide_predictions`: Get tide predictions for a specific station
   - Parameters:
     - `station_id`: 7-digit station ID
     - `begin_date`: Start date in yyyyMMdd format (optional)
     - `end_date`: End date in yyyyMMdd format (optional)
     - `datum`: Vertical datum (default: MLLW)
     - `time_zone`: Time zone (default: gmt)
     - `units`: Units of measurement (default: english)
     - `interval`: Prediction interval (default: hilo for high/low tides)

3. `get_station_info`: Get information about a specific station
   - Parameters:
     - `station_id`: 7-digit station ID

## Example Station IDs

- 9414290: San Francisco, CA
- 8518750: The Battery, NY
- 8557863: Rehoboth Beach, MD

## Running the Server

```bash
python server.py
```

## Using with Claude Desktop

To use this server with Claude Desktop, add it using the following configuration string:

```
python:/path/to/your/server.py
```

Replace `/path/to/your/server.py` with the actual path to your `server.py` file.

## License

MIT
