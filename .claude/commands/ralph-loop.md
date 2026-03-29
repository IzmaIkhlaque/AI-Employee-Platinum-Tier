# /ralph-loop

Run an autonomous multi-step task loop that iterates until a completion promise is output.

## Usage

```
/ralph-loop "task description" --max-iterations N --completion-promise "TOKEN"
```

## What It Does

1. Writes loop state to `.claude/hooks/ralph_state.json`
2. Executes the task prompt in this session
3. On each stop attempt, the `ralph_stop_check.py` hook:
   - Checks if `<promise>TOKEN</promise>` appears in the transcript
   - If **yes**: clears state, allows Claude to stop (success)
   - If **no** and iterations remain: re-injects the task prompt
   - If max iterations reached: stops regardless (safety)

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `"task"` | Yes | Task description to execute |
| `--max-iterations N` | Recommended | Stop after N iterations (default: 5) |
| `--completion-promise "TOKEN"` | Recommended | Token Claude outputs when done |

## Examples

```bash
/ralph-loop "Process all items in /Needs_Action and output <promise>VAULT_CLEAN</promise> when done." --max-iterations 5 --completion-promise "VAULT_CLEAN"

/ralph-loop "Generate CEO Briefing and output <promise>BRIEFING_DONE</promise> when complete." --max-iterations 10 --completion-promise "BRIEFING_DONE"
```

## Safety Rules

- Always set `--max-iterations` — never run unbounded
- Never include payment, deletion, or bulk-send actions in a loop
- Cancel active loop: delete `.claude/hooks/ralph_state.json`
- Monitor token usage — each iteration consumes API credits

## How to invoke

When the user runs `/ralph-loop "..." --max-iterations N --completion-promise "TOKEN"`:

1. Parse the task, max_iterations (default 5), and completion_promise from the arguments
2. Write `.claude/hooks/ralph_state.json`:
   ```json
   {
     "active": true,
     "task": "<the task prompt>",
     "completion_promise": "<TOKEN>",
     "max_iterations": N,
     "current_iteration": 1
   }
   ```
3. Immediately begin executing the task in this conversation
4. When all steps are done, output `<promise>TOKEN</promise>` to signal completion
5. The stop hook will detect this and clear the state

**IMPORTANT:** The completion promise must be output as: `<promise>TOKEN</promise>` — the hook scans for this exact string.
