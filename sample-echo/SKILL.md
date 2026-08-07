---
name: sample-echo
description: Echo back the arguments a script received. Use this to check how arguments reach a script, or to verify that a skill call works at all.
version: 0.1.0
min_isann: 0.1.0
author: isann
license: MIT
tags: [echo, arguments, args, params, parameters, verify, check, test, diagnostic, sample, example]
requires: [python]
run: sandbox
net: none
endpoint: local
tools: [bash]
scripts:
  plain: scripts/plain.py
  echo:
    entry: scripts/echo.py
    params:
      - name: text
        type: string
        required: true
        description: the text to print
      - name: times
        type: number
        description: how many times to repeat it (default 1)
---

# Sample Echo

Prints back the arguments it received, one per line. Useful for checking
that a call was built the way you meant it.

## When to use

Use this skill when the user wants to verify how arguments reach a
script, or asks for a quick check that a skill call works at all.

## How to run it

Run it with the **bash** tool by NAMING the declared script, not by
writing a shell command:

- `skill`: sample-echo
- `script`: echo
- `args`: ["hello"]

Write the skill's name, not its id.

`echo` takes its arguments IN ORDER:

1. `text` (required) - the text to print
2. `times` (optional) - how many times to repeat it

A wrong call is refused before the script runs: leave `text` out and the
answer says which argument is missing, by name.

## The other script

`plain` declares no arguments, so anything passed to it is accepted and
reaches the script unchecked:

- `skill`: sample-echo
- `script`: plain
- `args`: []

## Output

```
echo got 2 argument(s)
  1: hello
  2: 3
hello
hello
hello
```
