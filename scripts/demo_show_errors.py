"""Demo script — show errors.jsonl in a readable table."""
import json
from pathlib import Path

lines = Path("Logs/errors.jsonl").read_text(encoding="utf-8").strip().split("\n")
print(f"{'SEVERITY':<12} {'COMPONENT':<18} {'ERROR_TYPE':<22} {'RESOLVED'}")
print("-" * 65)
for line in lines:
    e = json.loads(line)
    print(f"{e['severity']:<12} {e['component']:<18} {e['error_type']:<22} resolved={e['resolved']}")
