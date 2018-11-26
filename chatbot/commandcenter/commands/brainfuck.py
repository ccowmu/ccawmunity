from ..command import Command
from ..eventpackage import EventPackage

# stolen from https://github.com/pocmo/Python-Brainfuck/blob/master/brainfuck.py

import sys

def evaluate(code):
  code     = cleanup(list(code))
  bracemap = buildbracemap(code)
  result   = ""

  cells, codeptr, cellptr = [0], 0, 0

  while codeptr < len(code):
    command = code[codeptr]

    if command == ">":
      cellptr += 1
      if cellptr == len(cells): cells.append(0)

    if command == "<":
      cellptr = 0 if cellptr <= 0 else cellptr - 1

    if command == "+":
      cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0

    if command == "-":
      cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255

    if command == "[" and cells[cellptr] == 0: codeptr = bracemap[codeptr]
    if command == "]" and cells[cellptr] != 0: codeptr = bracemap[codeptr]
    if command == ".": result += chr(cells[cellptr])
    if command == ",": pass # can't really do stdin in chat... or can we?
      
    codeptr += 1

  return result

def cleanup(code):
  return ''.join(filter(lambda x: x in ['.', ',', '[', ']', '<', '>', '+', '-'], code))

def buildbracemap(code):
  temp_bracestack, bracemap = [], {}

  for position, command in enumerate(code):
    if command == "[": temp_bracestack.append(position)
    if command == "]":
      start = temp_bracestack.pop()
      bracemap[start] = position
      bracemap[position] = start
  return bracemap

class BrainfuckCommand(Command):
    def __init__(self):
        self.name = "$brainfuck" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$brainfuck | brainfuck interpreter. \',\' instruction ignored. | usage: $brainfuck +[-[<<[+[--->]-[<<<]]]>>>-]>-.---.>..>.<<<<-.<+.>>>>>.>.<<.<-."
        
        self.author = "spacedog"
        self.last_updated = "Nov 26, 2018"

    def run(self, event_pack: EventPackage):
        return evaluate(''.join(event_pack.body[1:]))
