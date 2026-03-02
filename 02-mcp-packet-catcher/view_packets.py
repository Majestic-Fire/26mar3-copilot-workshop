"""
Packet Viewer — Pretty-print captured MCP packets from the JSONL log.

Usage:
  python view_packets.py                  # show all packets
  python view_packets.py --last 5         # show last 5 packets
  python view_packets.py --filter request # show only requests
  python view_packets.py --filter response # show only responses
"""

import json
import sys
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captured_packets.jsonl")

CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"
DIM = "\033[2m"


def main():
    if not os.path.exists(LOG_FILE):
        print("No captured packets yet. Run the packet catcher first!")
        return

    # Parse args
    filter_dir = None
    last_n = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--filter" and i + 1 < len(args):
            filter_dir = args[i + 1]
            i += 2
        elif args[i] == "--last" and i + 1 < len(args):
            last_n = int(args[i + 1])
            i += 2
        else:
            i += 1

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        packets = [json.loads(line) for line in f if line.strip()]

    if filter_dir:
        packets = [p for p in packets if p["direction"] == filter_dir]

    if last_n:
        packets = packets[-last_n:]

    if not packets:
        print("No matching packets.")
        return

    print(f"\n  📦 Showing {len(packets)} captured MCP packet(s)\n")

    for p in packets:
        direction = p["direction"]
        arrow = f"{CYAN}CLIENT ──▶ SERVER{RESET}" if direction == "request" else f"{YELLOW}SERVER ──▶ CLIENT{RESET}"
        pnum = p.get("packet_number", "?")
        print(f"{'='*60}")
        print(f"  {arrow}  {GREEN}#{pnum} {p['label']}{RESET}")
        if p.get("extra_info"):
            print(f"  {DIM}{p['extra_info']}{RESET}")
        print(f"  {DIM}{p['timestamp']}{RESET}")
        print(f"{'='*60}")
        print(json.dumps(p["message"], indent=2))
        print()


if __name__ == "__main__":
    main()
