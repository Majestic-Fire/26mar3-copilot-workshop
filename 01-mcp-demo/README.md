# 01 – FastMCP Demo Servers

Two MCP servers to demonstrate how Copilot uses tools under the hood.

**Start simple → then go real.**

---

## Server A: Simple MCP (`simple_server.py`)

A dead-simple server to prove MCP works. No external API — just fun tools.

🎤 **Hosts: Jemson & Winkie**

### Tools

| Tool | Description |
|------|-------------|
| `greet` | Greet someone (hosts get a special message!) |
| `get_hosts` | Who are today's workshop hosts? |
| `get_host_foods` | Favorite foods of Jemson or Winkie |
| `get_today` | Today's date & time in HKT |
| `get_agenda` | Workshop agenda |
| `get_fun_fact` | Random fun fact about Hong Kong |
| `roll_dice` | Roll a dice (default: d6) |
| `coin_flip` | Flip a coin |
| `add` | Add two numbers |

### Try it
```
"Greet Jemson"
"What's on the agenda today?"
"What are Winkie's favorite foods?"
"What day is it?"
"Roll a d20"
"Give me a fun fact about HK"
```

---

## Server B: HK Weather MCP (`server.py`)

The real deal — wraps the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk/weatherAPI/opendata/weather.php) into MCP tools with **live weather data**.

### Tools

| Tool | HKO dataType | Description |
|------|-------------|-------------|
| `get_local_weather_forecast` | `flw` | 本港地區天氣預報 — Local weather forecast |
| `get_9day_forecast` | `fnd` | 九天天氣預報 — 9-day weather forecast |
| `get_current_weather` | `rhrread` | 本港地區天氣報告 — Current weather report |
| `get_weather_warnings` | `warnsum` | 天氣警告一覽 — Warning summary |
| `get_weather_warning_details` | `warningInfo` | 詳細天氣警告資訊 — Detailed warning info |
| `get_special_weather_tips` | `swt` | 特別天氣提示 — Special weather tips |

All tools accept a `lang` parameter: `"en"` (English), `"tc"` (繁體中文), `"sc"` (简体中文).

## HKO API reference

- **Base URL**: `https://data.weather.gov.hk/weatherAPI/opendata/weather.php`
- **Method**: GET
- **Parameters**: `dataType` (required), `lang` (optional, default: `en`)
- **Returns**: JSON

## Setup

```bash
cd 01-mcp-demo
pip install -r requirements.txt
```

## Run standalone

```bash
# Simple server
python simple_server.py

# Weather server
python server.py
```

## Run via VS Code MCP client

The workspace `.vscode/mcp.json` has both servers configured:
- **`simple-mcp`** → `simple_server.py`
- **`hk-weather-mcp`** → `server.py`

Open **Copilot Agent Mode** in VS Code — enable whichever server you want to demo.

## Demo flow (comparison)

1. **Start with `simple-mcp`** — prove MCP works with basic tools
   - *"Who are the hosts?"* → Copilot calls `get_hosts`
   - *"What's Jemson's favorite food?"* → Copilot calls `get_host_foods`
   - "See? Copilot is calling our tools via MCP!"

2. **Switch to `hk-weather-mcp`** — now with real API data
   - *"What's the weather in HK right now?"* → Copilot calls `get_current_weather`
   - *"Show the 9-day forecast in 繁體中文"* → live HKO data!
   - "Same MCP protocol, but now fetching real weather data!"

3. **Turn on `mcp-with-inspector`** — see what's actually happening
   - Same weather tools, but every JSON-RPC packet is logged
- "Are there any active weather warnings?"
- "Get the detailed warning info"
- "Any special weather tips right now?"
- "香港今日天氣點呀？" (use lang=tc)
