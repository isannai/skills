---
name: sample-ls
description: List the files in a folder — name, size and modified time as JSON. Use this instead of `dir` or `ls`, which do not work in the sandbox.
version: 0.1.0
min_isann: 0.1.0
author: isann
license: MIT
run: sandbox
net: none
endpoint: local
requires: [python]
grant_args:
  ro: [args]
tags: [list, ls, dir, files, file, folder, folders, directory, directories, listing, browse, contents, tree]
tools: [bash]
scripts:
  ls: scripts/ls.py
---

# Sample LS

Lists a folder and returns JSON: one entry per item with its name, whether it is
a directory, its size in bytes, and when it was last modified.

## When to use

Whenever you need to see what files exist — before reading one, to find a file
whose exact name you were not told, or to check that something was written.

**Shell listing commands do not work here.** `dir` needs to open the disk volume,
which the sandbox blocks, and `ls` does not exist on Windows at all. Both fail
with a permission error that says nothing useful. Use this skill instead.

## How to run it

- `skill`: sample-ls
- `script`: ls
- `args`: the folder to list, e.g. `["C:\\Users\\me\\data"]`

Pass an ABSOLUTE path. The folder is opened read-only for that one call — the
skill reaches exactly the folder you named and nothing else.

`args` is the folder, and nothing else goes in it. It is not a command line:
there is no shell here, so `-c` or a `python …` string would just be read as the
name of a folder to list. The path is REQUIRED — an empty `args` fails rather
than listing something you did not ask for.

Do not set `cwd`. A skill always runs in its own folder; the folder you want to
LIST is the argument.

## Example

Input:

```bash
python scripts/ls.py C:\Users\me\data
```

Output:

```json
{
  "path": "C:\\Users\\me\\data",
  "count": 2,
  "entries": [
    {"name": "notes.txt", "dir": false, "size": 214, "modified": "2026-08-06T09:12:33"},
    {"name": "raw", "dir": true, "size": 0, "modified": "2026-08-05T18:40:02"}
  ]
}
```

## Notes

- Sorted directories first, then by name, so the output is stable between calls.
- A folder that does not exist, or one that was not opened for this call, fails
  with a message naming the path — not a bare permission error.
