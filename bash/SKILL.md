---
name: bash
description: Run shell commands and skill scripts inside the node's sandbox. Apply this whenever a task needs to execute a command, run a script, or process a file on this node.
version: 0.1.0
min_isann: 0.1.20
author: isann
license: MIT
endpoint: local
tools:
  - bash
tags: [core, execution, sandbox]
---

# Bash

Run a shell command with the **bash** tool. It executes inside this node's
OS-native sandbox (AppContainer on Windows, Landlock on Linux): the command gets
read+write to ONE working folder and nothing else - the install root and the
network are blocked unless explicitly opened.

## When to use

Whenever a task needs to actually DO something on the node - run a skill's
script, process a file, call an interpreter (python/node), or run any shell
command. Don't describe the command for the user to run; run it here.

## How to run a skill's script

This is the reliable pattern. A skill's own instructions tell you the command
(e.g. "run `python scripts/analyze.py <file>`"). To run it:

1. Pass the command as `cmd`.
2. Pass that skill's **name** (the heading it appears under in the Skills
   section) as `skill` - e.g. `sample-script`. Write the name, not the id.

```
bash{ skill: "sample-script", cmd: "python scripts/analyze.py sample.csv" }
```

Setting `skill` makes the command run IN that skill's folder, so relative paths
like `scripts/...` resolve automatically - you don't need `cwd`.

## Reaching files and the network

- The working folder is read+write. **Everything else is blocked** - the node's
  install folder, other folders, and the network.
- To read or write a folder OUTSIDE the working folder, name its absolute path in
  `grant_ro` (read-only) or `grant_rw` (read+write). A user-supplied file that
  lives elsewhere needs this.
- For network access (pip / apt / curl / git), set `net: "host"`. It is only
  honored when the node's sandbox permits it; otherwise it stays blocked.

```
bash{ cmd: "python -c 'print(1+1)'" }                       # bare command, private scratch folder
bash{ cmd: "wc -l data.csv", grant_ro: ["C:/Users/me/data"] }  # read an outside folder
bash{ cmd: "pip install pandas && python x.py", skill: "sample-script", net: "host" }
```

## Notes

- If a command fails (non-zero exit) or times out, bash returns the error - read
  it and fix the command or report it, rather than retrying blindly.
- If the sandbox worker is unavailable the run refuses outright - that is a node
  setup issue to report, not something to work around.
- Prefer one correct command over many probes; each call costs a turn.
