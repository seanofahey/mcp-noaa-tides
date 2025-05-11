from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create an MCP server instance
mcp = FastMCP("NOAA Tides")
logger.info("NOAA Tides MCP Server starting up...")

# Base URLs for NOAA CO-OPS APIs
DATA_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
METADATA_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations"

@mcp.tool()
async def get_water_levels(
    station_id: str,
    begin_date: str = None,
    end_date: str = None,
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
    logger.info(f"Getting water levels for station {station_id}")
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
            logger.info(f"Successfully retrieved water levels for station {station_id}")
            return response.json()
    except Exception as e:
        logger.error(f"Error getting water levels for station {station_id}: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_tide_predictions(
    station_id: str,
    begin_date: str = None,
    end_date: str = None,
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
    logger.info(f"Getting tide predictions for station {station_id}")
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
            logger.info(f"Successfully retrieved tide predictions for station {station_id}")
            return response.json()
    except Exception as e:
        logger.error(f"Error getting tide predictions for station {station_id}: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_station_info(station_id: str, expand: List[str] = None) -> Dict:
    """
    Get information about a specific station using the NOAA CO-OPS Metadata API.
    
    Args:
        station_id: The 7-digit station ID
        expand: List of additional resources to include (e.g., ["details", "sensors", "datums"])
    
    Returns:
        Dictionary containing station information including available products
    """
    logger.info(f"Getting station info for station {station_id}")
    try:
        # Construct the base URL with the station ID and .json extension
        url = f"{METADATA_URL}/{station_id}.json"
        
        # Add expand parameter to get products information
        params = {"expand": "products"}
        if expand:
            params["expand"] = f"products,{','.join(expand)}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Add available products information
            if "stations" in data and len(data["stations"]) > 0:
                station = data["stations"][0]
                available_products = {
                    "tide_predictions": any(
                        product["name"] == "Tide Predictions" 
                        for product in station.get("products", {}).get("products", [])
                    ),
                    "water_levels": station.get("observedst", False),
                    "currents": station.get("type") == "currents",
                    "is_active": station.get("observedst", False)
                }
                station["available_products"] = available_products
            
            logger.info(f"Successfully retrieved station info for station {station_id}")
            return data
    except Exception as e:
        logger.error(f"Error getting station info for station {station_id}: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def search_stations(query: str) -> Dict:
    """
    Search for stations by name or location.
    
    Args:
        query: Search term (e.g., city name, state, or station name)
    
    Returns:
        Dictionary containing matching stations
    """
    logger.info(f"Searching for stations matching: {query}")
    try:
        # First get all stations
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{METADATA_URL}.json")
            response.raise_for_status()
            data = response.json()
            
            # Split query into parts (e.g., "Cambridge, MD" -> ["cambridge", "md"])
            query_parts = [part.strip().lower() for part in query.split(',')]
            matching_stations = []
            
            if "stations" in data:
                for station in data["stations"]:
                    # Get station details
                    station_name = station.get("name", "").lower()
                    state = station.get("state", "").lower()
                    lat = station.get("lat", 0)
                    lng = station.get("lng", 0)
                    
                    # Check if any query part matches station name or state
                    matches = False
                    for part in query_parts:
                        if (part in station_name or 
                            part in state or 
                            (len(part) > 2 and part in station_name.split())):
                            matches = True
                            break
                    
                    if matches:
                        # Add available products information
                        available_products = {
                            "tide_predictions": any(
                                product["name"] == "Tide Predictions" 
                                for product in station.get("products", {}).get("products", [])
                            ),
                            "water_levels": station.get("observedst", False),
                            "currents": station.get("type") == "currents",
                            "is_active": station.get("observedst", False)
                        }
                        station["available_products"] = available_products
                        matching_stations.append(station)
            
            # Sort stations by relevance (exact matches first)
            matching_stations.sort(key=lambda x: (
                not any(part == x.get("name", "").lower() for part in query_parts),
                not any(part == x.get("state", "").lower() for part in query_parts)
            ))
            
            logger.info(f"Found {len(matching_stations)} matching stations")
            return {
                "stations": matching_stations,
                "count": len(matching_stations)
            }
    except Exception as e:
        logger.error(f"Error searching for stations: {str(e)}")
        return {"error": str(e)}

async def main():
    try:
        logger.info("Starting MCP server...")
        await mcp.run_stdio_async()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
