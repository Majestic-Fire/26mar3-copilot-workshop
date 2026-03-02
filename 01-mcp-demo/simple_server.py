"""
Simple MCP Server — Hello World Demo
======================================
A dead-simple MCP server to prove MCP works before moving to the real stuff.
Hosts: Jemson, Winkie

Run: python simple_server.py
"""

from datetime import datetime, timezone, timedelta
from fastmcp import FastMCP

mcp = FastMCP("Simple Workshop Server")

# ── Hosts ─────────────────────────────────────────────────────────────

HOSTS = ["Jemson", "Winkie"]

FAVORITE_FOODS = {
    "Jemson": ["Char Siu Rice 🍚", "Egg Tart 🥮", "Milk Tea 🧋"],
    "Winkie": ["Wonton Noodles 🍜", "Pineapple Bun 🍞", "Lemon Tea 🍋"],
}


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone! If you greet a host, you'll get a special message."""
    if name in HOSTS:
        return f"🎤 Hey! {name} is one of today's workshop hosts! Welcome everyone! 🎉"
    return f"Hello, {name}! Welcome to the Copilot Workshop 👋"


@mcp.tool()
def get_hosts() -> str:
    """Get the list of today's workshop hosts."""
    return f"🎤 Today's hosts: {', '.join(HOSTS)}"


@mcp.tool()
def get_host_foods(host: str) -> str:
    """Get a host's favorite foods. Try 'Jemson' or 'Winkie'."""
    foods = FAVORITE_FOODS.get(host)
    if not foods:
        available = ", ".join(FAVORITE_FOODS.keys())
        return f"Don't know {host}'s foods. Try: {available}"
    return f"🍽️ {host}'s favorite foods:\n" + "\n".join(f"  • {f}" for f in foods)


# ── Date & Time ───────────────────────────────────────────────────────

@mcp.tool()
def get_today() -> str:
    """Get today's date and time in Hong Kong (HKT)."""
    hkt = timezone(timedelta(hours=8))
    now = datetime.now(hkt)
    return (
        f"📅 Today is {now.strftime('%A, %B %d, %Y')}\n"
        f"🕐 Time: {now.strftime('%I:%M %p')} HKT"
    )


# ── Fun Lists ─────────────────────────────────────────────────────────

WORKSHOP_AGENDA = [
    "1️⃣  Intro — What is MCP?",
    "2️⃣  Demo — Simple MCP server (you are here!)",
    "3️⃣  Demo — HK Weather MCP (real API)",
    "4️⃣  Packet Catcher — See the protocol",
    "5️⃣  Copilot Skills — .prompt.md, .instructions.md, SKILL.md",
    "6️⃣  Q&A / Hands-on time",
]

HK_FUN_FACTS = [
    "🏙️ Hong Kong has over 9,000 skyscrapers — more than any other city!",
    "🚋 The Peak Tram has been running since 1888.",
    "🥢 Dim sum literally means 'touch the heart'.",
    "🌉 The Tsing Ma Bridge is one of the longest suspension bridges in the world.",
    "🎆 Victoria Harbour hosts one of the world's largest fireworks displays on NYE.",
    "🏠 Hong Kong's housing is the most expensive in the world per square foot.",
    "🐼 Giant pandas live at Ocean Park.",
]


@mcp.tool()
def get_agenda() -> str:
    """Get today's workshop agenda."""
    return "📋 Workshop Agenda:\n" + "\n".join(f"  {item}" for item in WORKSHOP_AGENDA)


@mcp.tool()
def get_fun_fact() -> str:
    """Get a random fun fact about Hong Kong."""
    import random
    return random.choice(HK_FUN_FACTS)


# ── Simple utilities ──────────────────────────────────────────────────

@mcp.tool()
def roll_dice(sides: int = 6) -> str:
    """Roll a dice with the given number of sides (default: 6)."""
    import random
    result = random.randint(1, max(1, sides))
    return f"🎲 Rolled a d{sides}: **{result}**"


@mcp.tool()
def coin_flip() -> str:
    """Flip a coin."""
    import random
    return f"🪙 {'Heads!' if random.random() < 0.5 else 'Tails!'}"


@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together. Simple math demo."""
    return f"🧮 {a} + {b} = {a + b}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple Workshop MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4002,
        help="Port for SSE transport (default: 4002)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse", host="localhost", port=args.port)
    else:
        mcp.run()
