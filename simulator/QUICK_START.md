# Simulator Quick Reference

## Start Using Right Now

```bash
# From project root
./simulate $echo hello world
./simulate $random 1 10
./simulate $karma test

# Interactive mode
./simulate
```

## Common Tasks

### Test a new command
```bash
./simulate $your_command arg1 arg2
```

### See all available commands
```bash
./simulate
>>> help
```

### Test command with multiple arguments
```bash
./simulate $addquote "@user:server: my quote"
```

### Test commands that use the database
```bash
./simulate $count
./simulate $karma something
```

### Use in scripts
```python
from chatbot.simulate import simulate

# Single run
result = simulate("$echo test")
print(result)

# Multiple commands
for cmd in ["$echo a", "$echo b", "$karma x"]:
    result = simulate(cmd)
    print(f"{cmd} -> {result}")
```

## Response Format

Responses are displayed with type indicators:

```
[CODE]
content here
[/CODE]

[RAINBOW]
content here
[/RAINBOW]

[BIG]
content here
[/BIG]

[STATE] event_type: {content}

Plain text response
```

## Keyboard Shortcuts (Interactive Mode)

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit simulator |
| `Up/Down Arrow` | Navigate command history (if supported by terminal) |
| `Tab` | Auto-complete (if supported by terminal) |

## Environment

- **Python**: Uses project's venv automatically (if exists)
- **Working Directory**: Can run from anywhere
- **Data**: All data is in-memory, cleared on exit
- **Timeout**: Commands timeout after 5 seconds (configurable in botconfig.py)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "command not found" | Run `chmod +x simulate` first |
| Missing dependencies | Run `pip install -r chatbot/requirements.txt` |
| Command hangs | Press `Ctrl+C` |
| No output | Add arguments to the command |

## What Works

✅ All commands in the `commandcenter/commands/` directory
✅ Commands that use the database
✅ All response types (text, code, rainbow, big, state)
✅ Command help and info
✅ Multiple sequential commands

## What Doesn't Work

❌ Commands that make real HTTP requests (will fail gracefully)
❌ Commands checking specific room permissions
❌ Real Matrix event subscriptions
❌ Listener/webhook systems

## Getting Help

- **In simulator**: Type `help` in interactive mode
- **Documentation**: See `SIMULATOR.md` in project root
- **Implementation details**: See `SIMULATOR_IMPLEMENTATION.md`
- **Code comments**: See `chatbot/simulate.py`

---

**That's it! The simulator is ready to use.**
