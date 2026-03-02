# 02 – MCP Packet Catcher / Inspector

## What is this?

A **transparent proxy** that sits between VS Code's MCP client and your real MCP server.  
It intercepts and logs **every JSON-RPC message** in both directions, so you can see exactly:

- 📤 What the client (Copilot) **sends** to the server (requests)
- 📥 What the server **returns** back (responses)
- The full JSON-RPC structure: `method`, `params`, `id`, `result`

## How it works

```
VS Code (Copilot)  ←──stdio──→  packet_catcher.py  ←──subprocess──→  real MCP server
                                       │
                                       ▼
                              captured_packets.jsonl
                              (+ live stderr output)
```

## Setup

```bash
cd 02-mcp-packet-catcher
pip install -r requirements.txt
```

## Usage

### 1. Run with the packet catcher wrapping your MCP server

Instead of pointing VS Code directly at your server, point it at the catcher:

```bash
python packet_catcher.py python ../01-mcp-demo/server.py
```

### 2. Watch packets live

The catcher prints every packet to **stderr** with colors and formatting.  
Just watch the terminal where you ran the command.

### 3. Review captured packets after

```bash
# Show all captured packets
python view_packets.py

# Show only the last 5
python view_packets.py --last 5

# Show only requests (client → server)
python view_packets.py --filter request

# Show only responses (server → client)
python view_packets.py --filter response
```

## VS Code integration

See `.vscode/mcp.json` — the `"mcp-with-inspector"` server entry wraps the demo server through the packet catcher.

## What you'll see

Example captured request (client → server):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_current_weather",
    "arguments": { "lang": "tc" }
  }
}
```

Example captured response (server → client):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "🌡️ Temperature:\n  Hong Kong Observatory: 28°C\n  ..." }
    ]
  }
}
```
