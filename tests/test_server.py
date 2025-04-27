import pytest
from httpx import Response
import json
from datetime import datetime
import server

# Sample response data
SAMPLE_WATER_LEVEL_DATA = {
    "metadata": {
        "id": "9414290",
        "name": "San Francisco",
        "lat": "37.8063",
        "lon": "-122.4659"
    },
    "data": [
        {
            "t": "2024-03-20 00:00",
            "v": "5.902",
            "s": "0.049",
            "f": "0,0,0,0"
        }
    ]
}

SAMPLE_PREDICTIONS_DATA = {
    "predictions": [
        {
            "t": "2024-03-20 00:00",
            "v": "5.902",
            "type": "H"
        }
    ]
}

SAMPLE_STATION_INFO = {
    "stations": [
        {
            "id": "9414290",
            "name": "San Francisco",
            "lat": "37.8063",
            "lon": "-122.4659",
            "state": "CA",
            "type": "waterlevels",
            "timezonecorr": "-8",
            "timezone": "LST/LDT"
        }
    ]
}

@pytest.mark.asyncio
async def test_get_water_levels(httpx_mock):
    """Test getting water level data."""
    # Mock the NOAA API response
    httpx_mock.add_response(
        url=f"{server.DATA_URL}?station=9414290&product=water_level&datum=MLLW&time_zone=gmt&units=english&format=json&application=MCP_NOAA_Tides&date=today",
        json=SAMPLE_WATER_LEVEL_DATA
    )
    
    result = await server.get_water_levels("9414290")
    assert result == SAMPLE_WATER_LEVEL_DATA
    assert result["metadata"]["id"] == "9414290"
    assert "data" in result
    assert len(result["data"]) > 0

@pytest.mark.asyncio
async def test_get_water_levels_with_dates(httpx_mock):
    """Test getting water level data with specific dates."""
    begin_date = "20240320"
    end_date = "20240321"
    
    httpx_mock.add_response(
        url=f"{server.DATA_URL}?station=9414290&product=water_level&datum=MLLW&time_zone=gmt&units=english&format=json&application=MCP_NOAA_Tides&begin_date={begin_date}&end_date={end_date}",
        json=SAMPLE_WATER_LEVEL_DATA
    )
    
    result = await server.get_water_levels("9414290", begin_date=begin_date, end_date=end_date)
    assert result == SAMPLE_WATER_LEVEL_DATA

@pytest.mark.asyncio
async def test_get_tide_predictions(httpx_mock):
    """Test getting tide predictions."""
    httpx_mock.add_response(
        url=f"{server.DATA_URL}?station=9414290&product=predictions&datum=MLLW&time_zone=gmt&units=english&interval=hilo&format=json&application=MCP_NOAA_Tides&date=today",
        json=SAMPLE_PREDICTIONS_DATA
    )
    
    result = await server.get_tide_predictions("9414290")
    assert result == SAMPLE_PREDICTIONS_DATA
    assert "predictions" in result
    assert len(result["predictions"]) > 0

@pytest.mark.asyncio
async def test_get_station_info(httpx_mock):
    """Test getting station information."""
    httpx_mock.add_response(
        url=f"{server.METADATA_URL}/9414290.json",
        json=SAMPLE_STATION_INFO
    )
    
    result = await server.get_station_info("9414290")
    assert result == SAMPLE_STATION_INFO
    assert "stations" in result
    assert result["stations"][0]["id"] == "9414290"

@pytest.mark.asyncio
async def test_get_station_info_with_expand(httpx_mock):
    """Test getting station information with expanded resources."""
    expanded_info = {
        "stations": [
            {
                "id": "9414290",
                "name": "San Francisco",
                "lat": "37.8063",
                "lon": "-122.4659",
                "state": "CA",
                "type": "waterlevels",
                "timezonecorr": "-8",
                "timezone": "LST/LDT",
                "details": {
                    "state": "CA",
                    "county": "San Francisco",
                    "timezone": "LST/LDT"
                },
                "sensors": [
                    {
                        "type": "water_level",
                        "status": "active"
                    }
                ]
            }
        ]
    }
    
    httpx_mock.add_response(
        url=f"{server.METADATA_URL}/9414290.json?expand=details,sensors",
        json=expanded_info
    )
    
    result = await server.get_station_info("9414290", expand=["details", "sensors"])
    assert result == expanded_info
    assert "stations" in result
    assert "details" in result["stations"][0]
    assert "sensors" in result["stations"][0]

@pytest.mark.asyncio
async def test_error_handling(httpx_mock):
    """Test error handling when API calls fail."""
    # Mock a failed API response
    httpx_mock.add_response(status_code=404)
    
    result = await server.get_water_levels("invalid_station")
    assert "error" in result
    assert isinstance(result["error"], str)

@pytest.mark.asyncio
async def test_invalid_parameters(httpx_mock):
    """Test handling of invalid parameters."""
    # Mock responses for invalid parameters
    httpx_mock.add_response(
        url=f"{server.DATA_URL}?station=9414290&product=water_level&datum=MLLW&time_zone=gmt&units=english&format=json&application=MCP_NOAA_Tides&date=today",
        status_code=400
    )
    
    httpx_mock.add_response(
        url=f"{server.DATA_URL}?station=invalid&product=water_level&datum=MLLW&time_zone=gmt&units=english&format=json&application=MCP_NOAA_Tides&date=today",
        status_code=400
    )
    
    # Test with invalid date format
    result = await server.get_water_levels("9414290", begin_date="invalid_date")
    assert "error" in result

    # Test with invalid station ID
    result = await server.get_water_levels("invalid")
    assert "error" in result 