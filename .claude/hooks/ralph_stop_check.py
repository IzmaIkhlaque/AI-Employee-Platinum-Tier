#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook
======================
Intercepts Claude Code's Stop event. If a ralph-loop is active and the
completion promise hasn't been output yet, this hook re-injects the task
prompt so Claude keeps iterating.

Hook input (stdin, JSON):
  {
    "session_id": "...",
    "transcript_path": "/path/to/transcript.jsonl",
    "stop_hook_active": true
  }

Exit codes:
  0  → allow Claude to stop (loop complete or no active loop)
  1  → block stop, re-inject prompt (Claude will continue)

State file: .claude/hooks/ralph_state.json
  {
    "active": true,
    "task": "...",
    "completion_promise": "VAULT_CLEAN",
    "max_iterations": 5,
    "current_iteration": 1,
    "session_id": "..."
  }
"""

import json
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent.parent
STATE_FILE = Path(__file__).parent / "ralph_state.json"


def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def check_transcript_for_promise(transcript_path: str, promise: str) -> bool:
    """Scan the session transcript for the completion promise string."""
    try:
        path = Path(transcript_path)
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8", errors="replace")
        return f"<promise>{promise}</promise>" in content
    except Exception:
        return False


def main() -> int:
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        return 0  # No valid input, allow stop

    state = load_state()
    if not state or not state.get("active"):
        return 0  # No active ralph-loop, allow stop

    transcript_path = hook_input.get("transcript_path", "")
    promise = state.get("completion_promise", "")
    task = state.get("task", "")
    max_iter = state.get("max_iterations", 5)
    current_iter = state.get("current_iteration", 1)

    # Check if promise was output in this session
    if promise and check_transcript_for_promise(transcript_path, promise):
        print(f"[Ralph] Promise <{promise}> found — loop complete after {current_iter} iteration(s). ✓", file=sys.stderr)
        clear_state()
        return 0  # Allow stop — we're done

    # Max iterations check
    if current_iter >= max_iter:
        print(f"[Ralph] Max iterations ({max_iter}) reached without promise. Stopping.", file=sys.stderr)
        clear_state()
        return 0  # Allow stop to prevent infinite loop

    # Re-inject: increment iteration and continue
    state["current_iteration"] = current_iter + 1
    save_state(state)

    print(
        f"[Ralph] Iteration {current_iter}/{max_iter} — promise <{promise}> not yet output. "
        f"Continuing...",
        file=sys.stderr,
    )

    # Output the continuation prompt to stdout — Claude Code injects this
    print(
        f"[Ralph Wiggum - Iteration {state['current_iteration']}/{max_iter}] "
        f"Continue working on the task. The completion promise "
        f"<promise>{promise}</promise> has not been output yet.\n\n"
        f"Remaining task:\n{task}"
    )
    return 1  # Block stop — keep iterating


if __name__ == "__main__":
    sys.exit(main())
