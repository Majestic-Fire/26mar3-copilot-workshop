# Copilot Workshop — MCP, Skills & Copilot Agent

A hands-on workshop exploring what happens under the hood with **GitHub Copilot Agent Mode**, **MCP (Model Context Protocol)**, and **Copilot Skills**.

## Workshop structure

```
26mar3-copilot-workshop/
│
├── 01-mcp-demo/                    ← FastMCP servers (simple + weather)
│   ├── simple_server.py            ← Simple MCP (greeting, hosts, agenda)
│   ├── server.py                   ← HK Weather MCP (6 live API tools)
│   ├── requirements.txt
│   └── README.md
│
├── 02-mcp-packet-catcher/          ← Protocol inspector / HTTP proxy
│   ├── packet_catcher.py           ← Reverse proxy that logs all JSON-RPC traffic
│   ├── view_packets.py             ← Pretty-print captured packets
│   ├── captured_packets.jsonl      ← Logged packets (auto-generated)
│   ├── requirements.txt
│   └── README.md
│
├── 03-skills-demo/                 ← Copilot Skills examples
│   ├── skills/
│   │   └── code-reviewer/SKILL.md  ← Packaged skill
│   ├── prompts/
│   │   ├── generate-api.prompt.md  ← Reusable prompt template
│   │   └── write-tests.prompt.md   ← Test generation prompt
│   ├── instructions/
│   │   └── python-style.instructions.md ← Auto-attached for .py files
│   ├── agents/
│   │   └── workshop-helper.agent.md     ← Custom agent definition
│   └── README.md
│
├── .vscode/
│   └── mcp.json                    ← VS Code MCP client configuration (SSE)
│
└── README.md                       ← You are here
```

---

## Prerequisites

- **VS Code** with GitHub Copilot extension (agent mode enabled)
- **Python 3.11+**
- `pip install fastmcp`

---

## Quick Setup (3 terminals)

All MCP servers run on **localhost** with SSE transport. The packet catcher proxy sits in front and logs all traffic.

```
┌──────────┐       ┌──────────────────┐       ┌─────────────────────┐
│  VS Code │──────▶│  Packet Catcher  │──────▶│  Weather Server     │
│  Copilot │  :4000│  (proxy + logger)│  :4001│  (HK Observatory)   │
└──────────┘       │                  │       └─────────────────────┘
                   │                  │       ┌─────────────────────┐
                   │                  │──────▶│  Simple Server      │
                   │                  │  :4002│  (greeting, hosts)  │
                   └──────────────────┘       └─────────────────────┘
```

### Terminal 1 — HK Weather MCP Server (port 4001)
```bash
cd 01-mcp-demo
pip install -r requirements.txt
python server.py --transport sse --port 4001
```

### Terminal 2 — Simple MCP Server (port 4002)
```bash
cd 01-mcp-demo
python simple_server.py --transport sse --port 4002
```

### Terminal 3 — Packet Catcher Proxy (port 4000)
```bash
cd 02-mcp-packet-catcher
python packet_catcher.py
```

That's it! VS Code MCP client (`.vscode/mcp.json`) is already configured to connect through the proxy:
- `http://localhost:4000/weather/sse` → HK Weather server
- `http://localhost:4000/simple/sse` → Simple Workshop server

---

## Part 1 — MCP Under the Hood (Simple → Real)

> Folder: `01-mcp-demo/`

Two servers: start simple to prove MCP works, then level up to live weather data.

### Demo 1A: Simple MCP (`simple_server.py`)
Prove MCP works with zero external dependencies — just greeting, hosts, dates, and fun tools.

**🎤 Hosts: Jemson & Winkie**

| Tool | What it does |
|------|--------------|
| `greet` | Greet someone (hosts get special treatment) |
| `get_hosts` | Today's hosts |
| `get_host_foods` | Favorite foods of each host |
| `get_today` | Today's date & time (HKT) |
| `get_agenda` | Workshop agenda |
| `get_fun_fact` | Random HK fun fact |
| `roll_dice` / `coin_flip` / `add` | Simple utility tools |

Try: *"Who are the hosts?"*, *"What's Jemson's favorite food?"*, *"Roll a d20"*

### Demo 1B: HK Weather MCP (`server.py`)
Same MCP pattern, but now wrapping the **Hong Kong Observatory Open Data API** — real, live weather data!

| dataType | Dataset |
|----------|--------|
| `flw` | 本港地區天氣預報 (Local Weather Forecast) |
| `fnd` | 九天天氣預報 (9-Day Forecast) |
| `rhrread` | 本港地區天氣報告 (Current Weather Report) |
| `warnsum` | 天氣警告一覽 (Warning Summary) |
| `warningInfo` | 詳細天氣警告資訊 (Detailed Warning Info) |
| `swt` | 特別天氣提示 (Special Weather Tips) |

Try: *"What's the weather in HK right now?"*, *"Show the 9-day forecast in 繁體中文"*, *"Any active weather warnings?"*

### The comparison
> "See? Same `@mcp.tool()` pattern. The simple server returns hardcoded data. The weather server calls a real API. Copilot doesn't know the difference — it just calls tools via MCP."

---

## Part 2 — Packet Catcher (See the Protocol)

> Folder: `02-mcp-packet-catcher/`

The packet catcher is an **HTTP reverse proxy** that sits between VS Code and the MCP servers. Every JSON-RPC message is intercepted, logged, and forwarded.

### What you'll learn
- The exact JSON-RPC messages Copilot sends and receives
- The `initialize` → `tools/list` → `tools/call` lifecycle
- How parameters are serialized and results returned

### Demo flow
1. Start all 3 processes (see Quick Setup above)
2. Use Copilot as normal — every packet gets logged to the proxy terminal
3. Run `python view_packets.py` to pretty-print captured traffic
4. Walk through a full request/response cycle with the audience

### Viewing packets
```bash
python 02-mcp-packet-catcher/view_packets.py              # all packets
python 02-mcp-packet-catcher/view_packets.py --last 5     # last 5
python 02-mcp-packet-catcher/view_packets.py --filter request  # requests only
```

---

## Part 3 — Copilot Skills

> Folder: `03-skills-demo/`

Explore the different ways to teach Copilot domain-specific knowledge.

### What you'll learn
- **copilot-instructions.md** — repo-wide behavior rules
- **.prompt.md** — reusable prompt templates (invoke with `#`)
- **.instructions.md** — auto-attached instructions based on file patterns
- **.agent.md** — custom agent definitions with tool restrictions
- **SKILL.md** — packaged skills for discovery

### Demo flow
1. Show `copilot-instructions.md` and how it shapes all Copilot responses
2. Use `#generate-api` prompt in chat to scaffold an endpoint
3. Open a `.py` file → `python-style.instructions.md` auto-applies
4. Show the `SKILL.md` structure for packaging reusable skills

---

## VS Code MCP Configuration

The `.vscode/mcp.json` uses **SSE transport** through the packet catcher proxy:

| Server | URL | Upstream |
|--------|-----|----------|
| `simple-mcp` | `http://localhost:4000/simple/sse` | Simple server on `:4002` |
| `hk-weather-mcp` | `http://localhost:4000/weather/sse` | Weather server on `:4001` |

All traffic flows through the proxy, so every MCP message is captured automatically.

---

## Port Summary

| Port | Service |
|------|---------|
| `4000` | Packet Catcher proxy (what VS Code connects to) |
| `4001` | HK Weather MCP server |
| `4002` | Simple Workshop MCP server |

---

## HKO Weather API reference

- **Base URL**: `https://data.weather.gov.hk/weatherAPI/opendata/weather.php`
- **Method**: `GET`
- **Params**: `dataType` (required) + `lang` (optional: `en`/`tc`/`sc`)
- **Example**: `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc`
