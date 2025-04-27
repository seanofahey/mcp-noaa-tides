from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import sys
import asyncio

# Create an MCP server instance
mcp = FastMCP("NOAA Tides")

# Base URLs for NOAA CO-OPS APIs
DATA_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
METADATA_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations"

@mcp.tool()
async def get_water_levels(
    station_id: str,
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None,
    datum: str = "MLLW",
    time_zone: str = "gmt",
    units: str = "english"
) -> Dict:
    """
    Get water level data for a specific station.
    
    Args:
        station_id: The 7-digit station ID
        begin_date: Start date in yyyyMMdd format (optional)
        end_date: End date in yyyyMMdd format (optional)
        datum: Vertical datum (default: MLLW)
        time_zone: Time zone (default: gmt)
        units: Units of measurement (default: english)
    
    Returns:
        Dictionary containing water level data
    """
    try:
        params = {
            "station": station_id,
            "product": "water_level",
            "datum": datum,
            "time_zone": time_zone,
            "units": units,
            "format": "json",
            "application": "MCP_NOAA_Tides"
        }
        
        if begin_date and end_date:
            params["begin_date"] = begin_date
            params["end_date"] = end_date
        else:
            params["date"] = "today"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(DATA_URL, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_tide_predictions(
    station_id: str,
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None,
    datum: str = "MLLW",
    time_zone: str = "gmt",
    units: str = "english",
    interval: str = "hilo"
) -> Dict:
    """
    Get tide predictions for a specific station.
    
    Args:
        station_id: The 7-digit station ID
        begin_date: Start date in yyyyMMdd format (optional)
        end_date: End date in yyyyMMdd format (optional)
        datum: Vertical datum (default: MLLW)
        time_zone: Time zone (default: gmt)
        units: Units of measurement (default: english)
        interval: Prediction interval (default: hilo for high/low tides)
    
    Returns:
        Dictionary containing tide predictions
    """
    try:
        params = {
            "station": station_id,
            "product": "predictions",
            "datum": datum,
            "time_zone": time_zone,
            "units": units,
            "interval": interval,
            "format": "json",
            "application": "MCP_NOAA_Tides"
        }
        
        if begin_date and end_date:
            params["begin_date"] = begin_date
            params["end_date"] = end_date
        else:
            params["date"] = "today"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(DATA_URL, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_station_info(station_id: str, expand: Optional[List[str]] = None) -> Dict:
    """
    Get information about a specific station using the NOAA CO-OPS Metadata API.
    
    Args:
        station_id: The 7-digit station ID
        expand: List of additional resources to include (e.g., ["details", "sensors", "datums"])
    
    Returns:
        Dictionary containing station information
    """
    try:
        # Construct the URL with the station ID
        url = f"{METADATA_URL}/{station_id}.json"
        
        # Add expand parameter if provided
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}

async def main():
    try:
        await mcp.run_stdio_async()
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
