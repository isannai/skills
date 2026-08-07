---
name: sample-read
description: Read a text file and print its contents with line numbers. Use this to show a file, look inside a log, or check what a text file contains.
version: 0.1.0
min_isann: 0.1.0
author: isann
license: MIT
tags: [read, file, text, txt, log, cat, show, print, view, open, contents, lines]
requires: [python]
run: sandbox
net: none
endpoint: local
tools: [bash]
grant_args:
  ro: [args]
scripts:
  read:
    entry: scripts/read.py
    params:
      - name: path
        type: string
        required: true
        description: path to the text file to read
      - name: lines
        type: number
        description: how many lines to show (0 or omitted = all)
---

# Sample Read

Reads a text file and prints it with line numbers, after a short header
giving the path and the total line count.

## When to use

Use this skill when the user wants to see what is inside a text file, read
a log, or check the contents of a file they named.

## How to run it

Run it with the **bash** tool by NAMING the declared script, not by
writing a shell command:

- `skill`: sample-read
- `script`: read
- `args`: ["sample.txt"]

Write the skill's name, not its id.

`read` takes its arguments IN ORDER:

1. `path` (required) - path to the text file
2. `lines` (optional) - show only the first N lines

A bundled `sample.txt` is included for a quick test, so `sample.txt` works
as the path with nothing else set up.

For a file the user named, pass its ABSOLUTE path. The script opens it
read-only and never writes anything.

## Output

```
file  : sample.txt
lines : 3

   1 | The quick brown fox
   2 | jumps over
   3 | the lazy dog.
```

With `lines` set, the rest is summarized instead of printed:

```
file  : sample.txt
lines : 3

   1 | The quick brown fox
   2 | jumps over
... (1 more)
```

If the file does not exist the script says so and stops; that is a real
answer about the path, not a problem with the skill.
