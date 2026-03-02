"""
MCP Packet Catcher — HTTP Reverse Proxy
=========================================
A transparent HTTP proxy that sits between VS Code MCP clients and real
MCP servers (running with SSE transport on localhost). It logs every JSON-RPC
message in both directions so workshop attendees can see exactly what the
protocol looks like under the hood.

Supports multiple upstream MCP servers under path prefixes:
  /weather/*  →  HK Weather MCP server  (port 4001)
  /simple/*   →  Simple Workshop server  (port 4002)

Architecture:
  VS Code  <──HTTP──>  packet_catcher.py (:4000)  <──HTTP──>  MCP servers (:4001, :4002)

Usage:
  # 1. Start the MCP servers with SSE transport
  python ../01-mcp-demo/server.py --transport sse --port 4001
  python ../01-mcp-demo/simple_server.py --transport sse --port 4002

  # 2. Start this proxy (captures both)
  python packet_catcher.py --port 4000

  # 3. Point VS Code MCP clients to:
  #    http://localhost:4000/weather/sse   (HK Weather)
  #    http://localhost:4000/simple/sse    (Simple Workshop)

All captured packets are:
  1. Printed to stderr with colors (watch live in the terminal)
  2. Appended to captured_packets.jsonl in this folder
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone

import httpx
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import StreamingResponse, Response
import uvicorn

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captured_packets.jsonl")

# ANSI colors for terminal output
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"

packet_count = 0


def log_packet(direction: str, raw: str, extra_info: str = ""):
    """Log a single JSON-RPC packet to stderr and to the log file."""
    global packet_count
    packet_count += 1
    timestamp = datetime.now(timezone.utc).isoformat()

    # Try to pretty-print JSON
    try:
        parsed = json.loads(raw)
        pretty = json.dumps(parsed, indent=2)
    except (json.JSONDecodeError, TypeError):
        parsed = None
        pretty = str(raw)

    # Determine message type label
    if parsed and isinstance(parsed, dict):
        method = parsed.get("method", "")
        msg_id = parsed.get("id", "")
        params = parsed.get("params", {})

        if "result" in parsed or "error" in parsed:
            label = f"RESPONSE id={msg_id}"
            if "error" in parsed:
                err = parsed["error"]
                label += f" ERROR({err.get('code', '?')}): {err.get('message', '?')}"
            elif "result" in parsed:
                result = parsed["result"]
                if isinstance(result, dict):
                    keys = list(result.keys())[:5]
                    label += f" keys={keys}"
                elif isinstance(result, str) and len(result) > 80:
                    label += f" (string, {len(result)} chars)"
        elif method:
            label = method
            if msg_id:
                label += f" (id={msg_id})"
            if method == "tools/call" and isinstance(params, dict):
                label += f" -> tool={params.get('name', '?')}"
            elif method == "initialize" and isinstance(params, dict):
                ci = params.get("clientInfo", {})
                label += f" client={ci.get('name', '?')}/{ci.get('version', '?')}"
        else:
            label = "unknown"
    else:
        label = "raw"

    # Color based on direction
    if direction == "request":
        arrow = f"{CYAN}{BOLD}CLIENT ──▶ SERVER{RESET}"
    else:
        arrow = f"{YELLOW}{BOLD}SERVER ──▶ CLIENT{RESET}"

    # Print to stderr (visible in terminal)
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  {arrow}  {GREEN}#{packet_count} {label}{RESET}", file=sys.stderr)
    if extra_info:
        print(f"  {BLUE}{extra_info}{RESET}", file=sys.stderr)
    print(f"  {DIM}{timestamp}{RESET}", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(pretty, file=sys.stderr)
    sys.stderr.flush()

    # Append to JSONL log file
    record = {
        "timestamp": timestamp,
        "direction": direction,
        "label": label,
        "packet_number": packet_count,
        "extra_info": extra_info,
        "message": parsed if parsed else raw,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def log_event(event_type: str, message: str):
    """Log an internal proxy event (connections, errors, etc.)."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"  {MAGENTA}[{event_type}]{RESET} {message}  {DIM}{ts}{RESET}", file=sys.stderr)
    sys.stderr.flush()


class MCPProxy:
    """HTTP reverse proxy that intercepts and logs MCP traffic for multiple upstreams."""

    def __init__(self, upstreams: dict, proxy_port: int):
        self.upstreams = upstreams
        self.proxy_port = proxy_port

    def _resolve(self, prefix: str):
        return self.upstreams.get(prefix)

    async def handle_sse(self, request: Request):
        """Proxy the SSE endpoint — the long-lived event stream."""
        prefix = request.path_params["prefix"]
        target_base = self._resolve(prefix)
        if not target_base:
            return Response(content=f"Unknown server: {prefix}", status_code=404)

        target_url = f"{target_base}/sse"
        proxy_host = request.headers.get("host", f"localhost:{self.proxy_port}")
        log_event("SSE", f"[{prefix}] Client connected, opening stream to {target_url}")

        async def generate():
            async with httpx.AsyncClient(timeout=None) as client:
                try:
                    async with client.stream("GET", target_url) as resp:
                        log_event("SSE", f"[{prefix}] Upstream connected (status {resp.status_code})")
                        current_event = ""
                        async for line in resp.aiter_lines():
                            if line.startswith("event:"):
                                current_event = line[6:].strip()
                                yield f"{line}\n"
                            elif line.startswith("data:"):
                                data = line[5:].strip()
                                if current_event == "endpoint":
                                    if data.startswith("/"):
                                        data = f"/{prefix}{data}"
                                    elif target_base in data:
                                        data = data.replace(
                                            target_base,
                                            f"http://{proxy_host}/{prefix}",
                                        )
                                    log_event("ENDPOINT", f"[{prefix}] Session URL: {data}")
                                elif current_event == "message":
                                    log_packet("response", data, f"[{prefix}] via SSE event")
                                else:
                                    log_event("SSE", f"[{prefix}] event={current_event} data={data[:200]}")
                                yield f"data: {data}\n"
                            elif line.startswith("id:") or line.startswith("retry:"):
                                yield f"{line}\n"
                            elif line.strip() == "":
                                current_event = ""
                                yield "\n"
                            else:
                                yield f"{line}\n"
                except httpx.ConnectError:
                    log_event("ERROR", f"[{prefix}] Cannot connect to upstream {target_base}")
                    yield f"event: error\ndata: Cannot connect to MCP server '{prefix}' at {target_base}\n\n"
            log_event("SSE", f"[{prefix}] Stream closed")

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def handle_messages(self, request: Request):
        """Proxy JSON-RPC message POSTs."""
        prefix = request.path_params["prefix"]
        target_base = self._resolve(prefix)
        if not target_base:
            return Response(content=f"Unknown server: {prefix}", status_code=404)

        body = await request.body()
        body_text = body.decode("utf-8", errors="replace")
        query = str(request.url.query) if request.url.query else ""

        log_packet("request", body_text, f"[{prefix}] POST /messages?{query}")

        target_url = f"{target_base}/messages/"
        if request.url.query:
            target_url += f"?{request.url.query}"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    target_url,
                    content=body,
                    headers={
                        "Content-Type": request.headers.get(
                            "content-type", "application/json"
                        )
                    },
                )
            except httpx.ConnectError:
                log_event("ERROR", f"[{prefix}] Cannot connect to upstream {target_base}")
                return Response(
                    content=json.dumps(
                        {"error": f"Cannot connect to MCP server '{prefix}' at {target_base}"}
                    ),
                    status_code=502,
                    media_type="application/json",
                )

        resp_body = resp.text
        if resp_body.strip():
            log_event("HTTP", f"[{prefix}] POST response: {resp.status_code} body={resp_body[:200]}")
        else:
            log_event("HTTP", f"[{prefix}] POST response: {resp.status_code} (accepted)")

        excluded = {"transfer-encoding", "content-encoding", "content-length", "connection"}
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
        return Response(content=resp.content, status_code=resp.status_code, headers=headers)

    async def handle_prefixed_path(self, request: Request):
        """Catch-all proxy for /{prefix}/{rest} paths."""
        prefix = request.path_params["prefix"]
        rest = request.path_params.get("rest", "")
        target_base = self._resolve(prefix)
        if not target_base:
            return Response(content=f"Unknown server: {prefix}", status_code=404)

        path = f"/{rest}" if rest else "/"
        query = f"?{request.url.query}" if request.url.query else ""
        method = request.method
        target_url = f"{target_base}{path}{query}"
        body = await request.body()

        if body:
            log_packet("request", body.decode("utf-8", errors="replace"), f"[{prefix}] {method} {path}{query}")
        else:
            log_event("HTTP", f"[{prefix}] -> {method} {path}{query}")

        skip = {"host", "transfer-encoding", "connection", "keep-alive"}
        fwd_headers = {k: v for k, v in request.headers.items() if k.lower() not in skip}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.request(method, target_url, content=body, headers=fwd_headers)
            except httpx.ConnectError:
                log_event("ERROR", f"[{prefix}] Cannot connect to upstream {target_url}")
                return Response(content=b"Bad Gateway", status_code=502)

        if resp.text.strip():
            try:
                json.loads(resp.text)
                log_packet("response", resp.text, f"[{prefix}] HTTP {resp.status_code} {path}")
            except (json.JSONDecodeError, TypeError):
                content_type = resp.headers.get("content-type", "")
                log_event("HTTP", f"[{prefix}] <- {resp.status_code} {content_type} ({len(resp.content)} bytes)")
        else:
            log_event("HTTP", f"[{prefix}] <- {resp.status_code}")

        excluded = {"transfer-encoding", "content-encoding", "content-length", "connection"}
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
        return Response(content=resp.content, status_code=resp.status_code, headers=headers)

    async def handle_index(self, request: Request):
        """Show available MCP server endpoints."""
        lines = ["MCP Packet Catcher — Available servers:\n"]
        for prefix, url in self.upstreams.items():
            lines.append(f"  /{prefix}/sse  →  {url}")
        return Response(content="\n".join(lines), media_type="text/plain")


def main():
    parser = argparse.ArgumentParser(
        description="MCP Packet Catcher — HTTP Reverse Proxy for multiple MCP servers"
    )
    parser.add_argument("--port", "-p", type=int, default=4000, help="Proxy listen port (default: 4000)")
    parser.add_argument("--weather-port", type=int, default=4001, help="HK Weather MCP server port (default: 4001)")
    parser.add_argument("--simple-port", type=int, default=4002, help="Simple Workshop MCP server port (default: 4002)")
    parser.add_argument("--host", type=str, default="localhost", help="Target host for MCP servers (default: localhost)")
    args = parser.parse_args()

    upstreams = {
        "weather": f"http://{args.host}:{args.weather_port}",
        "simple": f"http://{args.host}:{args.simple_port}",
    }

    proxy = MCPProxy(upstreams, args.port)

    app = Starlette(
        routes=[
            Route("/", proxy.handle_index),
            Route("/{prefix}/sse", proxy.handle_sse),
            Route("/{prefix}/messages", proxy.handle_messages, methods=["POST"]),
            Route("/{prefix}/messages/", proxy.handle_messages, methods=["POST"]),
            Route("/{prefix}/{rest:path}", proxy.handle_prefixed_path, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
        ],
    )

    # Banner
    print(f"\n{'*'*70}", file=sys.stderr)
    print(f"  {BOLD}MCP Packet Catcher — Multi-Server HTTP Reverse Proxy{RESET}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"  {GREEN}Proxy listening:{RESET}   http://localhost:{args.port}", file=sys.stderr)
    print(f"", file=sys.stderr)
    for prefix, url in upstreams.items():
        print(f"  {GREEN}{prefix}:{RESET}", file=sys.stderr)
        print(f"    Upstream:  {url}", file=sys.stderr)
        print(f"    SSE URL:   http://localhost:{args.port}/{prefix}/sse", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"  {GREEN}Log file:{RESET}  {LOG_FILE}", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"  {CYAN}Quick start:{RESET}", file=sys.stderr)
    print(f"    1) python ../01-mcp-demo/server.py --transport sse --port {args.weather_port}", file=sys.stderr)
    print(f"    2) python ../01-mcp-demo/simple_server.py --transport sse --port {args.simple_port}", file=sys.stderr)
    print(f"    3) python packet_catcher.py --port {args.port}", file=sys.stderr)
    print(f"    4) VS Code MCP client URLs:", file=sys.stderr)
    print(f"         http://localhost:{args.port}/weather/sse", file=sys.stderr)
    print(f"         http://localhost:{args.port}/simple/sse", file=sys.stderr)
    print(f"{'*'*70}\n", file=sys.stderr)

    # Clear previous log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        pass

    uvicorn.run(app, host="localhost", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
