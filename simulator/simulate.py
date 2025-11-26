#!/usr/bin/env python3

"""
CClub Chatbot Command Simulator

This script allows you to test bot commands without needing:
- A running Matrix server
- A Redis instance
- Network connectivity

Usage:
    Command mode:       python3 simulate.py $echo hello world
    Interactive mode:   python3 simulate.py
    
Or use the wrapper from the project root:
    ./simulate $echo hello world
    ./simulate

Features:
    - Mock Redis backend (in-memory storage)
    - Full command execution through the command system
    - Support for all response types (text, code, rainbow, big, state)
    - Interactive REPL for testing multiple commands
made by Grand Admiral Thrawn <3
"""

import sys
import os
import shlex
import re
from unittest.mock import Mock, MagicMock

# Ensure the chatbot directory is in Python's import path
# This allows imports to work correctly regardless of where the script is run from
# Note: This script is in simulator/, but commandcenter is in chatbot/
chatbot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'chatbot')
sys.path.insert(0, chatbot_dir)

# =============================================================================
# REDIS MOCKING
# =============================================================================

# Mock the redis module before importing any commands
# This prevents connection errors when commands try to use the database
sys.modules['redis'] = MagicMock()

# Create a mock Redis instance that stores data in memory
class MockRedis:
    """
    An in-memory mock of Redis that mimics the redis-py API.
    
    This allows all commands to use their Redis database operations without
    needing a running Redis server. All data is stored in memory for the
    duration of the script.
    
    Key features:
    - Stores all data types: strings, lists, sets, sorted sets, hashes
    - Returns bytes like real Redis (for compatibility with command code)
    - Implements enough of the Redis API for all bot commands
    """
    
    def __init__(self):
        """Initialize the in-memory data store."""
        self.data = {}
    
    def _encode(self, value):
        """
        Convert a value to bytes, matching Redis behavior.
        
        Real Redis always returns bytes, so we encode strings to bytes
        to ensure commands work correctly (e.g., wordle.py calls .decode())
        """
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode()
        return str(value).encode()
    
    def set(self, key, value):
        self.data[key] = self._encode(value)
        return True
    
    def get(self, key):
        val = self.data.get(key)
        return val if val is not None else None
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    def setnx(self, key, value):
        """Set value only if key doesn't exist. Returns 1 if set, 0 if not."""
        if key not in self.data:
            self.data[key] = self._encode(value)
            return 1
        return 0
    
    def incr(self, key):
        if key not in self.data:
            self.data[key] = 0
        self.data[key] = int(self.data[key]) + 1
        return self.data[key]
    
    def incrby(self, key, amount):
        if key not in self.data:
            self.data[key] = 0
        self.data[key] = int(self.data[key]) + amount
        return self.data[key]
    
    def lpush(self, key, value):
        """Push a value to the left (beginning) of a list."""
        if key not in self.data:
            self.data[key] = []
        if not isinstance(self.data[key], list):
            self.data[key] = []
        self.data[key].insert(0, self._encode(value))
        return len(self.data[key])
    
    def rpush(self, key, value):
        """Push a value to the right (end) of a list."""
        if key not in self.data:
            self.data[key] = []
        if not isinstance(self.data[key], list):
            self.data[key] = []
        self.data[key].append(self._encode(value))
        return len(self.data[key])
    
    def lpop(self, key):
        """Pop and return a value from the left (beginning) of a list."""
        if key in self.data and isinstance(self.data[key], list) and self.data[key]:
            return self.data[key].pop(0)
        return None
    
    def rpop(self, key):
        """Pop and return a value from the right (end) of a list."""
        if key in self.data and isinstance(self.data[key], list) and self.data[key]:
            return self.data[key].pop()
        return None
    
    def llen(self, key):
        """Get the length of a list."""
        if key in self.data and isinstance(self.data[key], list):
            return len(self.data[key])
        return 0
    
    def lset(self, key, index, value):
        """Set a value at a specific index in a list."""
        if key in self.data and isinstance(self.data[key], list):
            self.data[key][index] = value
            return True
        return False
    
    def lrem(self, key, num, value):
        """Remove num occurrences of value from a list."""
        if key in self.data and isinstance(self.data[key], list):
            count = 0
            while value in self.data[key] and (num == 0 or count < num):
                self.data[key].remove(value)
                count += 1
            return count
        return 0
    
    def lindex(self, key, index):
        """Get a value at a specific index in a list."""
        if key in self.data and isinstance(self.data[key], list):
            try:
                return self.data[key][index]
            except IndexError:
                return None
        return None
    
    def lrange(self, key, start, end):
        """Get a range of values from a list."""
        if key in self.data and isinstance(self.data[key], list):
            return self.data[key][start:end+1 if end >= 0 else None]
        return []
    
    def ltrim(self, key, start, end):
        """Trim a list to a specific range."""
        if key in self.data and isinstance(self.data[key], list):
            self.data[key] = self.data[key][start:end+1 if end >= 0 else None]
            return True
        return False
    
    def sadd(self, key, value):
        """Add a value to a set."""
        if key not in self.data:
            self.data[key] = set()
        if not isinstance(self.data[key], set):
            self.data[key] = set()
        self.data[key].add(self._encode(value))
        return 1
    
    def srem(self, key, value):
        """Remove a value from a set."""
        if key in self.data and isinstance(self.data[key], set):
            enc_value = self._encode(value)
            if enc_value in self.data[key]:
                self.data[key].remove(enc_value)
                return 1
        return 0
    
    def sismember(self, key, value):
        """Check if a value is in a set."""
        if key in self.data and isinstance(self.data[key], set):
            return 1 if self._encode(value) in self.data[key] else 0
        return 0
    
    def smembers(self, key):
        """Get all members of a set."""
        if key in self.data and isinstance(self.data[key], set):
            return self.data[key]
        return set()
    
    def srandmember(self, key):
        """Get a random member from a set."""
        if key in self.data and isinstance(self.data[key], set) and self.data[key]:
            import random
            return random.choice(list(self.data[key]))
        return None
    
    def sunion(self, *keys):
        """Get the union of multiple sets."""
        result = set()
        for key in keys:
            if key in self.data and isinstance(self.data[key], set):
                result = result.union(self.data[key])
        return result
    
    def zadd(self, key, mapping):
        """Add values with scores to a sorted set."""
        if key not in self.data:
            self.data[key] = {}
        if not isinstance(self.data[key], dict):
            self.data[key] = {}
        for k, v in mapping.items():
            self.data[key][self._encode(k)] = v
        return len(mapping)
    
    def zrem(self, key, value):
        """Remove a value from a sorted set."""
        if key in self.data and isinstance(self.data[key], dict):
            if value in self.data[key]:
                del self.data[key][value]
                return 1
        return 0
    
    def zrange(self, key, start, end):
        """Get a range of values from a sorted set."""
        if key in self.data and isinstance(self.data[key], dict):
            items = sorted(self.data[key].items(), key=lambda x: x[1])
            result = items[start:end+1 if end >= 0 else None]
            return [item[0] for item in result]
        return []
    
    def hset(self, key, mapping_or_key, value=None):
        """Set one or more hash fields."""
        if key not in self.data:
            self.data[key] = {}
        if value is not None:
            self.data[key][mapping_or_key] = self._encode(value)
            return 1
        else:
            for k, v in mapping_or_key.items():
                self.data[key][k] = self._encode(v)
            return len(mapping_or_key)
    
    def hget(self, key, field):
        """Get a hash field value."""
        if key in self.data and isinstance(self.data[key], dict):
            return self.data[key].get(field)
        return None
    
    def hgetall(self, key):
        """Get all fields and values from a hash."""
        if key in self.data and isinstance(self.data[key], dict):
            return self.data[key]
        return {}
    
    def hincrby(self, key, field, amount):
        """Increment a hash field by a specific amount."""
        if key not in self.data:
            self.data[key] = {}
        if field not in self.data[key]:
            self.data[key][field] = 0
        self.data[key][field] = int(self.data[key][field]) + amount
        return self.data[key][field]
    
    def hdel(self, key, field):
        """Delete a hash field."""
        if key in self.data and isinstance(self.data[key], dict):
            if field in self.data[key]:
                del self.data[key][field]
                return 1
        return 0

# Patch the redis module in command.py
import commandcenter.command.command as command_module
command_module.redis = MockRedis()

# =============================================================================
# IMPORTS
# =============================================================================

from commandcenter.commander import Commander
from commandcenter.eventpackage import EventPackage
from commandcenter import command
import botconfig


def safe_split(text):
    """
    Safely convert input string into a list of arguments.
    
    This mimics the safe_split function from chat.py, handling:
    - Unclosed quotes (replaces last " with ')
    - Quoted strings with spaces
    - Proper shell-like parsing
    
    Args:
        text: Input command string
        
    Returns:
        List of parsed arguments
    """
    pattern = re.compile(r'\"(?!.*\")')
    text = pattern.sub("'", text) if text.count('"') % 2 != 0 else text

    s = shlex.shlex(text, posix=True)
    s.quotes = '"'
    s.whitespace_split = True
    s.commenters = ''
    return list(s)


def format_response(response):
    """
    Convert a CommandResponse to a displayable string.
    
    Formats the response based on its type:
    - CODE: Wrapped in [CODE] tags
    - RAINBOW: Wrapped in [RAINBOW] tags
    - BIG: Wrapped in [BIG] tags
    - STATE: Shows the state change
    - TEXT: Regular text
    
    Args:
        response: A CommandResponse object or string
        
    Returns:
        Formatted string for display
    """
    if isinstance(response, command.CommandCodeResponse):
        return f"[CODE]\n{response.text}\n[/CODE]"
    elif isinstance(response, command.CommandRainbowResponse):
        return f"[RAINBOW]\n{response.text}\n[/RAINBOW]"
    elif isinstance(response, command.CommandBigResponse):
        return f"[BIG]\n{response.text}\n[/BIG]"
    elif isinstance(response, command.CommandStateResponse):
        return f"[STATE] {response.type}: {response.content}"
    elif isinstance(response, str):
        return response
    else:
        return str(response)


def simulate(command_string, sender="@test_user:test.server", room_id="!test:test.server"):
    """
    Simulate running a command without Matrix connection.
    
    This is the core function that executes a command as if it were sent
    in a Matrix chat room. It creates a mock EventPackage and passes it
    through the command system.
    
    Args:
        command_string: The full command string (e.g., "$echo hello world")
        sender: Mock sender ID (default: test user)
        room_id: Mock room ID (default: test room)
    
    Returns:
        The command response (or None if no response)
        
    Examples:
        >>> simulate("$echo hello")
        "hello"
        >>> simulate("$random 1 10")
        "7"
    """
    # Initialize commander if not already done
    if not hasattr(simulate, 'commander'):
        simulate.commander = Commander(botconfig.command_prefix, botconfig.command_timeout)

    commander = simulate.commander
    
    # Parse command
    argv = safe_split(command_string)
    if not argv:
        return None
    
    command_str = argv[0]
    
    # Create mock event package
    event_pack = EventPackage(
        body=argv,
        room_id=room_id,
        sender=sender,
        event={}
    )
    
    # Run the command
    result = commander.run_command(command_str, event_pack)
    
    return result


def interactive_mode():
    """
    Run an interactive command simulation session (REPL).
    
    This starts a read-eval-print loop where you can:
    - Type commands and see their output
    - Type 'help' to see all available commands
    - Type 'quit' to exit
    
    This is useful for testing multiple commands without restarting
    the script or writing them as command-line arguments.
    """
    print("=" * 60)
    print("CClub Chatbot Command Simulator")
    print("=" * 60)
    print(f"Command prefix: {botconfig.command_prefix}")
    print("Type 'help' for command list, 'quit' to exit\n")
    
    commander = Commander(botconfig.command_prefix, botconfig.command_timeout)
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print(commander.get_help_all())
                continue
            
            # Simulate the command
            result = simulate(user_input)
            
            if result is not None:
                formatted = format_response(result)
                print(f"{formatted}\n")
            else:
                print("(No response)\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    """
    Main entry point for the simulator.
    
    If command-line arguments are provided, runs that command.
    Otherwise, starts the interactive mode (REPL).
    """
    if len(sys.argv) > 1:
        # Run command from command line arguments
        command_string = " ".join(sys.argv[1:])
        result = simulate(command_string)
        if result is not None:
            print(format_response(result))
    else:
        # Interactive mode
        interactive_mode()


if __name__ == '__main__':
    main()
