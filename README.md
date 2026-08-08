# Skills

A **skill** is a folder of know-how: a `SKILL.md` telling the agent how to do
something, plus any scripts it needs. The agent loop injects the text into its
prompt; a declared script is what actually runs.

A skill only DECLARES the tools it uses - it never defines or injects them.

```
<name>/SKILL.md          the skill; scripts/ alongside it
       |
       | isann skill pull
       v
<install-root>/artifacts/addon/skills/<name>/
```

## Layout of this repo

```
base/SKILL.md                   core: baseline operating rules
bash/SKILL.md                   core: how to use the bash tool
search_capabilities/SKILL.md    core: how to find tools you were not shown

examples/sample-ls/             list a folder as JSON
examples/sample-read/           read a text file with line numbers
examples/sample-echo/           echo back the arguments a script received
examples/sample-script/         analyze a CSV (row count + column stats)
examples/sample-check/          analyze a CSV and echo the arguments back
```

The three at the root are the **core** skills a node ships with. They are here
so you can read and fork them; a working node already has them.

The five under `examples/` are runnable demonstrations. Each is a folder with a
`SKILL.md` and a `scripts/` directory - `sample-read` and `sample-script` also
carry a sample data file so they work with no setup.

## File format

`SKILL.md` is markdown with a YAML frontmatter header. There is no separate
manifest: the header IS the metadata.

```markdown
---
name: sample-ls
description: List the files in a folder - name, size and modified time as JSON.
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
tags: [list, ls, dir, files, folder, directory]
tools: [bash]
scripts:
  ls: scripts/ls.py
---

# Sample LS

(the body: what it does, when to use it, how to call it)
```

Key fields:

| Field | Meaning |
|---|---|
| `description` | One line. This is what search matches on - write it for a reader who does not know the skill exists. |
| `tags` | Synonyms. The body must be English, so put other wordings here. |
| `tools` | Tools the skill needs, e.g. `[bash]`. Declaration only. |
| `scripts` | `name: path` - what `skill call` and the `bash` tool can run. |
| `run` | `sandbox` (OS-native isolation) or `host`. |
| `requires` | Interpreters the script needs, e.g. `[python]`. |
| `grant_args.ro` | Which arguments are opened read-only for that one call. |

### SKILL.md must be printable ASCII

Non-ASCII bytes are rejected at pull and at publish. The rule keeps search
tokenization deterministic - no unicode normalization traps - and it is a byte
scan, so it also catches typographic punctuation. These four slip in by habit,
from editors and from AI assistants, and look almost identical to the ASCII they
should be:

| Character | Replace with |
|---|---|
| em dash, U+2014 | `-` |
| en dash, U+2013 | `-` |
| horizontal ellipsis, U+2026 | `...` |
| curly quotes, U+2018/2019/201C/201D | `'` and `"` |

`---` (three plain hyphens, the frontmatter delimiter) is fine.

To find them before you commit:

```bash
grep -nP '[^\x00-\x7F]' SKILL.md      # any line with a non-ASCII byte
```

The error names the offending byte and its offset:

```
non-ASCII byte 0xE2 at offset 62 - asset files must be printable ASCII
```

Non-English know-how belongs in `tags` as synonyms, not in the body.

The rule applies to `SKILL.md` only; a script's comments are not scanned.

## Install

A skill is folder-shaped: **the whole folder is one asset.** Paste the folder's
address straight from the GitHub page.

```bash
# the folder = the skill (SKILL.md + scripts/ + data files)
isann skill pull https://github.com/isannai/skills/tree/main/examples/sample-ls

# just the SKILL.md, no scripts
isann skill pull https://github.com/isannai/skills/blob/main/examples/sample-ls/SKILL.md
```

Use the folder form for anything with a `scripts/` directory - the file form
installs the prose only, and `skill call` will then fail with nothing to run.

`SKILL.md` must be present in the folder. That is checked BEFORE anything
downloads, so a wrong path costs one request and leaves no folder behind:

```
isann: skill pull: isannai/skills has no SKILL.md
  looked in: https://github.com/isannai/skills/tree/<commit-sha>
  found:     LICENSE, README.md, base/SKILL.md, examples/sample-ls/SKILL.md
```

The ref is pinned to its commit, so every file comes from one snapshot and the
recorded source names the exact commit installed.

Re-pulling an installed name reports `[skip]` and exits 0; `-force` re-pulls.

```bash
isann skill pull <url> --name my-ls     # local folder name (default: last URL segment)
isann skill pull <url> --token <PAT>    # private repo / raise the 60/h rate limit
```

## Use

```bash
isann skill list                       # installed skills, and the loadouts using each
isann skill inspect sample-ls          # raw SKILL.md + provenance
isann skill call sample-ls ls C:\some\folder
```

A skill is injected into the agent's prompt **iff it is a member of an active
loadout** - there is no separate "active skill" set:

```bash
isann loadout add work --includes sample-ls
```

`skill call` runs a declared script directly, which is the quickest way to check
that a pull brought the scripts along.

## Publish to the hub

```bash
isann skill push sample-ls --version 1.0.0 --summary "list a folder as JSON"
isann skill price sample-ls --free      # pricing IS the listing
```

Run `isann auth unlock` first - the upload is signed with your owner wallet.
Publishing re-checks the ASCII rule before distributing.

## Writing a skill

Full guide: **[docs/skills.md](docs/skills.md)** - frontmatter field by field,
writing a body a model can act on, `scripts:` and the argument contract,
`endpoint:` and selling, and the mistakes people actually hit.

Start from the shared rules in **[docs/overview.md](docs/overview.md)**: where
files live, the ASCII constraint, how IDs work, and the difference between being
injected and being allowed to run.

The short version:

```
my-skill/
  SKILL.md          required - the header + the know-how
  scripts/run.py    optional - what actually executes
  sample.csv        optional - data the skill ships with
```

Commit the folder. There is no index file to update - the tree is the catalog.

## Documentation

| | |
|---|---|
| [docs/overview.md](docs/overview.md) | Capabilities overview - shared rules for skills and tools, and P2P execution |
| [docs/skills.md](docs/skills.md) | Writing a skill (this repo's subject) |
| [docs/tools.md](docs/tools.md) | Writing a tool - the things a skill declares in `tools:` |