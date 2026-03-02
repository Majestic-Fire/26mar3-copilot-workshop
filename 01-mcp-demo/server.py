"""
FastMCP Demo Server — Hong Kong Observatory Weather API
=========================================================
An MCP server built with FastMCP that wraps the HKO Open Data Weather API.
Demonstrates what happens under the hood when Copilot calls an MCP tool.

HKO API docs: https://data.weather.gov.hk/weatherAPI/opendata/weather.php
Supported datasets:
  - flw:     Local Weather Forecast (本港地區天氣預報)
  - fnd:     9-Day Weather Forecast (九天天氣預報)
  - rhrread: Current Weather Report (本港地區天氣報告)

Run directly:  python server.py
Or via MCP client in VS Code (see .vscode/mcp.json)
"""

import json
from typing import Literal
from urllib.request import urlopen, Request
from urllib.error import URLError

from fastmcp import FastMCP

mcp = FastMCP("HK Weather MCP Server")

API_BASE = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
Lang = Literal["en", "tc", "sc"]


def _fetch(data_type: str, lang: str = "en") -> dict | list | str:
    """Call the HKO API and return parsed JSON."""
    url = f"{API_BASE}?dataType={data_type}&lang={lang}"
    req = Request(url, headers={"User-Agent": "MCP-Workshop/1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            raw_response = resp.read().decode("utf-8")
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError:
                return f"Error: invalid JSON response from HKO API. Raw response: {raw_response}"
    except URLError as e:
        return f"Error fetching data from HKO API: {e}"
    except json.JSONDecodeError:
        return "Error: invalid JSON response from HKO API."


# ── Tool 1: Local Weather Forecast (flw) ─────────────────────────────

@mcp.tool()
def get_local_weather_forecast(lang: Lang = "en") -> str:
    """
    Get the local weather forecast for Hong Kong (本港地區天氣預報).
    Returns general situation, forecast description, outlook, and TC info if any.
    lang: 'en' for English, 'tc' for Traditional Chinese, 'sc' for Simplified Chinese.
    """
    data = _fetch("flw", lang)
    if isinstance(data, str):
        return data

    parts = []
    if data.get("generalSituation"):
        parts.append(f"📋 General Situation:\n{data['generalSituation']}")
    if data.get("tcInfo"):
        parts.append(f"🌀 Tropical Cyclone Info:\n{data['tcInfo']}")
    if data.get("fireDangerWarning"):
        parts.append(f"🔥 Fire Danger Warning:\n{data['fireDangerWarning']}")
    if data.get("forecastPeriod"):
        parts.append(f"🕐 Forecast Period: {data['forecastPeriod']}")
    if data.get("forecastDesc"):
        parts.append(f"🌤️ Forecast:\n{data['forecastDesc']}")
    if data.get("outlook"):
        parts.append(f"🔭 Outlook:\n{data['outlook']}")
    if data.get("updateTime"):
        parts.append(f"⏰ Updated: {data['updateTime']}")

    return "\n\n".join(parts) if parts else json.dumps(data, ensure_ascii=False, indent=2)


# ── Tool 2: 9-Day Weather Forecast (fnd) ─────────────────────────────

@mcp.tool()
def get_9day_forecast(lang: Lang = "en") -> str:
    """
    Get the 9-day weather forecast for Hong Kong (九天天氣預報).
    Returns daily forecasts with temperature, humidity, wind, rain probability, and weather icon.
    lang: 'en' for English, 'tc' for Traditional Chinese, 'sc' for Simplified Chinese.
    """
    data = _fetch("fnd", lang)
    if isinstance(data, str):
        return data

    lines = []

    # Soil temperature
    if data.get("soilTemp"):
        for s in data["soilTemp"]:
            lines.append(f"🌱 Soil Temp ({s.get('place', '?')}): {s.get('value')} {s.get('unit', '')} at depth {s.get('depth', {}).get('value', '?')} {s.get('depth', {}).get('unit', '')}")

    # Sea temperature
    if data.get("seaTemp"):
        for s in data["seaTemp"]:
            lines.append(f"🌊 Sea Temp ({s.get('place', '?')}): {s.get('value')} {s.get('unit', '')}")

    if lines:
        lines.append("")

    forecasts = data.get("weatherForecast", [])
    for day in forecasts:
        date = day.get("forecastDate", "?")
        week = day.get("week", "")
        weather = day.get("forecastWeather", "")
        max_t = day.get("forecastMaxtemp", {}).get("value", "?")
        min_t = day.get("forecastMintemp", {}).get("value", "?")
        max_rh = day.get("forecastMaxrh", {}).get("value", "?")
        min_rh = day.get("forecastMinrh", {}).get("value", "?")
        wind = day.get("forecastWind", "")
        psr = day.get("PSR", "")
        icon = day.get("ForecastIcon", "")

        lines.append(f"📅 {date} ({week})")
        lines.append(f"   {weather}")
        lines.append(f"   🌡️ {min_t}–{max_t}°C  💧 {min_rh}–{max_rh}%")
        lines.append(f"   💨 {wind}")
        if psr:
            lines.append(f"   🌧️ Rain probability: {psr}")
        if icon:
            lines.append(f"   Icon: {icon}")
        lines.append("")

    if data.get("updateTime"):
        lines.append(f"⏰ Updated: {data['updateTime']}")

    return "\n".join(lines) if lines else json.dumps(data, ensure_ascii=False, indent=2)


# ── Tool 3: Current Weather Report (rhrread) ─────────────────────────

@mcp.tool()
def get_current_weather(lang: Lang = "en") -> str:
    """
    Get the current weather report for Hong Kong (本港地區天氣報告).
    Returns temperature, humidity, rainfall, UV index, warnings, and lightning data.
    lang: 'en' for English, 'tc' for Traditional Chinese, 'sc' for Simplified Chinese.
    """
    data = _fetch("rhrread", lang)
    if isinstance(data, str):
        return data

    parts = []

    # Temperature
    temp_data = data.get("temperature", {}).get("data", [])
    if temp_data:
        unit = temp_data[0].get("unit", "C")
        temps = [f"  {t['place']}: {t['value']}°{unit}" for t in temp_data if t.get("value") is not None]
        if temps:
            parts.append("🌡️ Temperature:\n" + "\n".join(temps))

    # Humidity
    hum_data = data.get("humidity", {}).get("data", [])
    if hum_data:
        hums = [f"  {h['place']}: {h['value']}%" for h in hum_data if h.get("value") is not None]
        if hums:
            parts.append("💧 Humidity:\n" + "\n".join(hums))

    # Rainfall
    rainfall = data.get("rainfall", {})
    rain_data = rainfall.get("data", [])
    if rain_data:
        rains = []
        for r in rain_data:
            max_val = r.get("max", 0)
            min_val = r.get("min", 0)
            unit = r.get("unit", "mm")
            rains.append(f"  {r.get('place', '?')}: {min_val}–{max_val} {unit}")
        if rains:
            start = rainfall.get("startTime", "")
            end = rainfall.get("endTime", "")
            parts.append(f"🌧️ Rainfall ({start} → {end}):\n" + "\n".join(rains))

    # UV index
    uv = data.get("uvindex")
    uv_data = uv.get("data", []) if isinstance(uv, dict) else []
    if uv_data:
        uvs = [f"  {u.get('place', '?')}: {u.get('value', '?')} ({u.get('desc', '')})" for u in uv_data]
        if uvs:
            parts.append("☀️ UV Index:\n" + "\n".join(uvs))

    # Lightning
    lightning = data.get("lightning")
    lightning_data = lightning.get("data", []) if isinstance(lightning, dict) else []
    if lightning_data:
        strikes = [f"  ⚡ {l.get('place', '?')}" for l in lightning_data if l.get("occur")]
        if strikes:
            parts.append("⚡ Lightning detected:\n" + "\n".join(strikes))

    # Warning messages
    warnings = data.get("warningMessage", [])
    if warnings and any(w for w in warnings):
        parts.append("⚠️ Warnings:\n" + "\n".join(f"  {w}" for w in warnings if w))

    # Special weather tips
    tips = data.get("specialWxTips", [])
    if tips:
        parts.append("💡 Special Weather Tips:\n" + "\n".join(f"  {t}" for t in tips))

    # TC message
    tc = data.get("tcmessage", [])
    if tc:
        parts.append("🌀 Tropical Cyclone:\n" + "\n".join(f"  {m}" for m in tc if m))

    # Icon
    icons = data.get("icon", [])
    if icons:
        parts.append(f"🖼️ Weather icon(s): {icons}")

    if data.get("updateTime"):
        parts.append(f"⏰ Updated: {data['updateTime']}")

    return "\n\n".join(parts) if parts else json.dumps(data, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HK Weather MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4001,
        help="Port for SSE transport (default: 4001)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse", host="localhost", port=args.port)
    else:
        mcp.run()
