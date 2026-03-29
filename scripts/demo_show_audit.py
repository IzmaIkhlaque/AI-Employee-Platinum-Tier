"""Demo script — show audit.jsonl in a readable table."""
import json
from pathlib import Path

lines = Path("Logs/audit.jsonl").read_text(encoding="utf-8").strip().split("\n")
print(f"Total entries: {len(lines)}")
print()
for line in lines:
    e = json.loads(line)
    print(f"{e['ts'][11:19]}  {e.get('actor', 'system'):<7}  {e['action']}")
