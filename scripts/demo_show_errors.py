"""Demo script — show errors.jsonl in a readable table."""
import json
from pathlib import Path

lines = Path("Logs/errors.jsonl").read_text(encoding="utf-8").strip().split("\n")
print(f"{'SEVERITY':<12} {'COMPONENT':<20} {'ERROR':<40} {'RESOLVED'}")
print("-" * 85)
for line in lines:
    if not line.strip():
        continue
    e = json.loads(line)
    severity  = e.get("severity", e.get("action", "unknown")).upper()
    component = e.get("component", e.get("platform", "unknown"))
    error     = e.get("error_type", e.get("error", ""))[:38]
    resolved  = e.get("resolved", e.get("action_required", "see log"))
    resolved_str = str(resolved)[:10] if isinstance(resolved, bool) else "see log"
    print(f"{severity:<12} {component:<20} {error:<40} resolved={resolved_str}")
