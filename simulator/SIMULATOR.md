# CClub Chatbot Simulator

A tool to test chatbot commands locally without needing a running Matrix server or Redis instance.

## Quick Start

### Setup (One-time)

From the project root:

```bash
# Install Python dependencies (if not already done)
pip install -r chatbot/requirements.txt

# Make the wrapper script executable
chmod +x simulate
```

### Usage

**Command mode** (test a single command):
```bash
./simulate $echo hello world
./simulate $random 1 10
./simulate $wordle
```

**Interactive mode** (test multiple commands):
```bash
./simulate
>>> $echo hello
>>> $random 1 10
>>> help
>>> quit
```

## How It Works

### Architecture

The simulator consists of three main components:

1. **MockRedis** - An in-memory Redis implementation that mimics the redis-py API
2. **Command System** - The existing command system from the chatbot (unchanged)
3. **Simulator Interface** - Entry point that connects commands to the mock environment

### Why This Works

- **No external services**: All data is stored in memory, so you don't need Redis running
- **Compatible with existing code**: Commands don't need modification; they work the same way
- **Full feature support**: All Redis operations (lists, sets, hashes, sorted sets, etc.) are supported

### File Structure

```
ccawmunity/
├── simulate                          # Wrapper script (bash)
├── chatbot/
│   └── simulate.py                   # Main simulator (Python)
├── chatbot/commandcenter/
│   ├── commands/                     # All bot commands
│   ├── commander/commander.py        # Command dispatcher
│   └── command/command.py            # Command base class
```

## For Developers

### How to Use Programmatically

```python
from chatbot.simulate import simulate

# Test a command
result = simulate("$echo hello world")
print(result)  # "hello world"

# With custom sender and room
result = simulate(
    "$echo test",
    sender="@user:matrix.org",
    room_id="!room:matrix.org"
)
```

### Adding New Commands

Commands work the same in the simulator as in production. No special setup needed!

Just run:
```bash
./simulate $your_new_command
```

### Understanding the Code

**Key sections in `chatbot/simulate.py`:**

- **Lines 1-30**: Module docstring and imports
- **Lines 32-340**: MockRedis class (in-memory database)
  - String operations (set, get, incr, etc.)
  - List operations (push, pop, range, etc.)
  - Set operations (add, remove, members, etc.)
  - Hash operations (hset, hget, hincrby, etc.)
  - Sorted set operations (zadd, zrange, etc.)
- **Lines 342-357**: Redis patching (replaces real Redis with mock)
- **Lines 358-400**: Utility functions (safe_split, format_response)
- **Lines 401-425**: `simulate()` function (core simulation logic)
- **Lines 426-460**: `interactive_mode()` function (REPL)
- **Lines 461-475**: `main()` function (entry point)

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"

The dependencies aren't installed. Run:
```bash
pip install -r chatbot/requirements.txt
```

### "ConnectionError: redis"

The mock Redis isn't being used. Make sure you're running `./simulate` or running from the chatbot directory:
```bash
cd chatbot
python3 simulate.py $echo test
```

### Command hangs or times out

Some commands might have long timeouts or infinite loops. Press `Ctrl+C` to interrupt.

## Limitations

- **Network commands won't work**: Commands that make HTTP requests (like `$led`, `$door`, etc.) will fail or return mocked data
- **Room context**: The simulator uses a fake room ID and sender, so commands that check specific rooms may behave differently
- **Real Matrix features**: Commands that rely on actual Matrix protocol features won't work

## Testing Multiple Commands

Create a file with commands:

```bash
# test_commands.txt
$echo hello
$random 1 10
$test
```

Then pipe it:
```bash
cat test_commands.txt | ./simulate
```

## Contributing

If you add new Redis operations to a command, update MockRedis to support them:

1. Open `chatbot/simulate.py`
2. Find the MockRedis class
3. Add the new method following the existing pattern
4. Make sure to use `self._encode()` for return values to match Redis behavior

## Questions?

Check the docstrings in `simulate.py` or run:
```bash
./simulate
>>> help
```
