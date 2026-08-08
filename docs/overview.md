# Capabilities Overview

> What this node can do, and who uses it how. Start here for the big picture and
> the shared rules, then move to the guide you need.

---

## 1. The three things

| | What it is | Where it lives |
|---|---|---|
| **Tool** | a function the model **calls** | `tools.json` |
| **Skill** | know-how the model **reads** | `SKILL.md` |
| **MCP** | one **door** for using this node from outside | built into the node |

**Tools and skills are the capabilities. MCP is one of several doors into
them.**

```
        Tool  +  Skill          <- the capabilities are here
              ^
   -----------+-----------
   |          |          |
 this node   MCP     another node
 isann CLI  Claude Code  P2P (--nodes / endpoint)
```

**Whichever door you come through, the same tools and the same skills run.** MCP
is the door you open when you want to work from a chat window on your laptop,
and **the other two work fine without it.**

### A tool creates a capability

Read a file, fetch a page, start a container - **things the node could not do
before.** The model calls it like a function.

### A skill creates no capability

It is written know-how about an existing tool: **when to reach for it, in what
order, and how to read the result.** It goes into the system prompt for the
model to read.

```
tools but no skills
   the model can run a shell, but guesses every time what to run
   in THIS project

skills but no tools
   the model knows what should happen, but has no hands
```

### MCP is a door outward, and it is optional

Attach MCP and other clients - Claude Code, for instance - use this node's tools
and skills as they are. It does not add capability; it adds **one more entrance**
to the capability you already had.

**You do not have to attach it.** The node runs agents by itself:

```bash
isann agent run "analyze sample.csv" --engine llama
isann skill call <id> analyze sample.csv
isann tool call bash "ls -al"
```

### You can use another node's capabilities (P2P)

A capability does not have to live on your node. **Nodes connect directly**, so
you can call a skill that sits on someone else's node - and that is also how a
capability is **sold**.

```bash
isann skill list --nodes <node>          # what that node sells (no wallet needed to look)
isann skill call <id> analyze 0xA9f3...   # runs there; only the result comes back
```

**Where it runs is decided by the skill, not by the caller.** One line in
`SKILL.md`:

```yaml
endpoint: local        # this node's sandbox (the default when omitted)
endpoint: 0xB1c4...    # that node
```

So **the calling command is identical whether it is local or remote.** You do
not add `--nodes`.

---

## 2. P2P - running on another node

What happens behind one `skill call`. You can use it without knowing, but it is
worth knowing **what travels and what does not.**

```
my node                                             seller node
  isann skill call <id> analyze 0xA9f3...
        |
        | 1. where does this skill run?  ->  endpoint: 0xB1c4...
        | 2. find that node, open the blocked door   (rendezvous server)
        | 3. direct connection                        isannd
        |------------------ arguments only ----------->  |
        |   { skill: <id>, script: "analyze",             | 4. is it listed for sale?
        |     args: ["0xA9f3..."] }                       | 5. run it isolated
        |<----------------- result only ---------------   |    scripts/analyze.py
            { stdout: "...", node: "0xb1c4..." }
```

**That is everything that moves.**

| | |
|---|---|
| Goes out | **the arguments, and nothing else.** Not your files, not your conversation |
| Comes back | **stdout, plus the ID of the node that actually ran it** |
| **Never moves** | **the script.** It stays on the seller's node - that is their business |

**There is no server in the middle.** The rendezvous server only does step 2 -
tell you the address and open the blocked door. The request and the result flow
between the two nodes only, encrypted (HTTP/3). Being behind a router is fine.

**You can tell it is really them.** A node ID is a **wallet address**, not a
domain, and requests carry signatures. Ownership cannot change hands the way a
domain can, and nobody in the middle can answer in their place. That is why
`endpoint` will not accept a URL.

**It runs by their rules.** Their isolation settings and their grants apply, not
yours, and the only thing that can run is a **script the skill declared in
advance**. You cannot run arbitrary commands over there.

**The caller needs two things:**

```bash
isann auth unlock       # a wallet to sign with - the call has to be attributable
```

and the other side must have **listed that skill for sale.** Something installed
but not listed cannot be called from outside.

> Browsing needs no wallet. `isann skill list --nodes <node>` is **reading a
> price list**, so it requires no signature - you decide after looking.

### This is not the same as borrowing a GPU

Both mention `--nodes`, which makes them easy to confuse. They are different
things.

| Command | Runs on the other node | Runs on mine |
|---|---|---|
| `isann agent run --nodes B` | **model inference only** | every tool and skill |
| `isann skill call <id> ...` (endpoint is B) | **that skill's script** | everything else |
| `isann tool call <name> --nodes B` | that tool | - (only on nodes you operate) |

```
agent run --nodes B    you borrow B's GPU.       the capability is yours
skill call (endpoint)  you buy B's capability.   the script is B's
```

`tool call --nodes` goes through a different door from the other two: it works
only on **nodes where you are the operator** (your second node, a team node),
never a stranger's. The only door open to strangers is a **listed skill**.

---

## 3. Where to start

| What you want | Guide |
|---|---|
| See what already works | "Try it first" below |
| Teach an agent a team convention or procedure | [Writing a Skill](skills.md) |
| Make the node able to do something new | [Writing a Tool](tools.md) |
| Use this node from a chat window | MCP guide |
| Use another node's capability | [Writing a Skill](skills.md) section 7 |
| Build a capability and sell it | [Writing a Skill](skills.md) section 7, section 10 |

### Try it first

These work straight after install. **You do not have to build anything, and MCP
is not needed.**

```bash
isann skill list                            # what is here (this is where IDs come from)
isann skill call <id> analyze sample.csv    # run the bundled sample-script
isann agent run "analyze sample.csv" --engine llama
```

The build order is:

```
1. Tool    make the hands       (only when the capability is missing)
2. Skill   how to use them      (most work starts here)
```

> Most people start at **step 2**. `bash` and the other defaults are already
> installed, so a great deal is possible with skills alone.

**MCP is not in that order.** It is not a build step but a choice - after
everything is built - about whether to open outward. Skip it and the commands
above, plus P2P, still work.

---

## 4. Shared rules

These apply **identically to tools and skills**, and are not repeated in the
individual guides.

### 4.1 One asset is one folder

**Your install already contains examples.** Opening them shows the rules at a
glance.

```
<install-root>/artifacts/addon/
  skills/
    base/                 SKILL.md      <- this one file IS the skill
    bash/                 SKILL.md
    search_capabilities/  SKILL.md
    sample-script/        SKILL.md      <- one that carries a script
                          scripts/analyze.py
                          sample.csv
  tools/
    bash/                 tools.json    <- this one file IS the tool bundle
    isann/                tools.json
    search_capabilities/  tools.json
```

**The folder name is the asset's name**, and the unit an operator turns on and
off.

**Keep scripts and data files inside that folder.** Execution is isolated, and
the only folder the sandbox opens is the asset's own. A declaration pointing
outside is refused outright.

```yaml
scripts:
  analyze: scripts/analyze.py     # relative to the folder
```

> `base`, `bash` and `search_capabilities` in that same directory are **not
> samples** - they are the working defaults. Do not delete them.

If you genuinely need a file outside the folder there is a way to open it; see
the `grant_ro` / `grant_args` sections of each guide.

> Placing or editing a file takes effect **immediately.** The node re-scans the
> folder on each call, so no restart.

### 4.2 Printable ASCII only

`SKILL.md` and `tools.json` **may not contain a single non-ASCII character.**
The whole file is scanned at install and at publish, and rejected:

```
non-ASCII byte 0xEC at offset 42 - asset files must be printable ASCII
```

**This is a deliberate product decision.** Assets are found by search, and
search splits text into words to index it. Those splitting rules differ by
language, and the same character can be stored several ways (unicode
normalization), so **two strings that look identical are treated as different**.
Indexing in one language removes that trap.

The cost is real: **you cannot put non-English know-how in an asset body.** That
trade-off was accepted knowingly.

> **Hiding non-English search terms in tags does not work either.** The check
> scans the raw bytes before the file is parsed, so any field fails the same way.

For a question asked in another language to reach your asset, the model has to
translate it into an English search phrase. What you can do about that is section 4.6.

### 4.3 An ID is the hash of the file

```
ID = sha256(file contents)
```

It is not a number assigned from the name or version. **Fixing one typo produces
a different ID.**

Day to day you call things by name and never notice - until **something else
points at that ID**:

| What breaks | Where |
|---|---|
| a sale listing goes `MISSING` | [Writing a Skill](skills.md) section 8 |
| an execution policy points at nothing | [Writing a Tool](tools.md) section 8 |
| the "same" asset on two nodes diverges | [Writing a Skill](skills.md) section 7 |

**This is a mechanism, not a bug.** When you use someone else's asset and they
later swap the contents, calls arriving with the old ID **fail to resolve rather
than quietly running something else.**

```
quietly runs something else   <- the worst outcome
just fails                    <- what was chosen
```

> So finish the content first, then register. That way one edit is enough.

### 4.4 Creating it does not show it to the model

Placing the file and the model knowing about it are **separate**. There are two
routes.

**A. Put it in a loadout.** Always visible.

```bash
isann loadout add research --includes sample-script,search_capabilities
isann loadout use research
```

Names, not IDs; comma-separated for several.

**B. Let it be discovered by search.** Surfaces only when needed.

When the model asks "is there anything that can do X", it appears in the results
and is usable from the next turn. This keeps a loadout lean while leaving the
rest reachable.

| | |
|---|---|
| **loadout** | what you always use, loaded **up front** |
| **search** | what you occasionally use, found **then** |

Check what actually went in:

```bash
isann agent run "..." --engine llama --trace skills,tools
```

### 4.5 Being visible and being allowed to run are different

Appearing in a list does not mean execution is permitted. **Two separate gates:**

```
injection   does the model know about it?     loadout, search
execution   is it allowed to run?             policy
```

In particular, **a skill pulling in a tool is not a grant.** Writing "this skill
uses that tool" in `SKILL.md` brings the tool along, but the operator still
grants execution separately:

```bash
isann policy add --rule execution --tool <tool-ref> user
```

**Installing someone else's asset does not make what is written inside it
suddenly runnable.** This separation is what prevents that.

### 4.6 Ten or more tags, two or three synonyms per concept

Search scans these words. **A word that is not here will not find it.**

The problem is that **the author cannot know which word the user will type.**
One says "CSV", another "spreadsheet", another "table", another "Excel file".
List one and you lose the rest.

```yaml
# too few - "spreadsheet" finds nothing
tags: [csv]

# padded with the same word - still one concept
tags: [csv, csv-file, csvfile, csv_reader, read-csv]

# synonyms per concept, ten or more
tags: [csv, spreadsheet, excel, table, tabular,      # what it works on
       data, analyze, analysis, statistics, stats,   # what it does
       summary, rows, columns]                       # what comes out
```

Three angles make the list easy to fill:

| Angle | Question | Example |
|---|---|---|
| Subject | what does it work on | `csv` `spreadsheet` `excel` `table` |
| Action | what does it do | `analyze` `analysis` `summarize` `statistics` |
| Result | what comes out | `summary` `rows` `columns` `report` |

The description is searched too. Put there what tags cannot carry.

---

## 5. Frequently confused

### "Should I write a tool or a skill?"

Check whether existing tools can already do the job:

```bash
isann tool list
```

If a shell command does it, **a skill is enough.** Write a new tool to wrap an
outside API, or a program you run the same way every time.

### "Name or ID?"

**People and models use names; machines use IDs.**

Have `SKILL.md` bodies and prompts use **names**. IDs are long hashes that models
mistype; the node substitutes the exact ID just before execution.

The places you write an ID yourself are the ones that must pin a target -
**sale listings and policies.**

### "Why is what I made never called?"

Check in order:

```
1. is it listed?          isann skill list / isann tool list
2. was it injected?       the skills / tools line under --trace
3. does the description say WHEN to use it?
4. is execution granted?
```

Blocked at 2 is the loadout. At 3 it is your writing. At 4 it is policy.
