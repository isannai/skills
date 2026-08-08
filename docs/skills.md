# Writing a Skill

> A **skill is one file of know-how** - "here is how to use these tools". The
> file is `SKILL.md`, and the agent reads it **into its system prompt.**

This is the end-to-end guide. **Read the [Capabilities Overview](overview.md)
first** - the difference from tools, where files live, the ASCII constraint, how
IDs work, injection vs execution permission, and how P2P execution works are all
there and are not repeated here.

---

## 1. A skill is read

**A skill creates no capability.** It is written know-how about tools that
already exist: **when to reach for one, in what order, and how to read the
result.** That text goes into the system prompt.

### 1.1 But a skill can also be called

Being read is a skill's original shape. You can also make **the scripts inside a
skill callable by name.** One line - `scripts:` - is the whole difference.

```
prose form      the body says "run python scripts/x.py" and the model
                assembles the command from that sentence

scripts form    the author publishes callable names in advance and the
                caller just picks one from the list
```

**The prose form is the original and is still perfectly valid.** Write the body
well and the model builds and runs the command itself.

The scripts form is needed when **the caller is not a model**. A person at a
command line, or another node over the network, has no model to read the prose
and assemble a command. Then you need a shape where **handing over one name is
enough.** Section 6 is entirely about that.

> **`SKILL.md` must be printable ASCII.** Not one non-ASCII character. See
> [Overview section 4.2](overview.md).

---

## 2. The smallest skill

```yaml
---
name: house-style
description: How this team writes commit messages.
---

# House Style

Commit messages use the imperative mood: "add X", not "added X".
Keep the subject under 60 characters.
```

**That is all.** No scripts, no tools to declare.

And it is already useful. While this skill is active the model **starts every
commit message knowing the rule**, so nobody has to add "write it in the
imperative" each time. Most of a skill's value lives here; scripts are an
optional layer on top.

**Team conventions, routine procedures, traps worth warning about** - all of
them are fine in this shape.

Two ways to install it, either is fine:

**1. Place the file**

```
<install-root>/artifacts/addon/skills/house-style/SKILL.md
```

**2. Or use the command**

```bash
isann skill create --name house-style --file house-style.md
```

Same result. The node re-scans the folder on each call, so **no restart.**

```bash
isann skill list
```

| | |
|---|---|
| **body-only skill** | method 2 is easier - no need to know the install root, and it creates the folder |
| **skill with scripts** | method 1 is natural - `create` only writes `SKILL.md`, so you would make `scripts/` by hand anyway |

Method 2 adds two guards: the **ASCII check runs now** rather than blowing up
later at publish time, and it **refuses to overwrite** an existing name without
`-force`.

---

## 3. File layout

Add scripts and it becomes a folder.

```
skills/
  sample-echo/
    SKILL.md                <- required. This one file IS the skill
    scripts/
      echo.py
      plain.py
    sample.txt              <- data it uses goes here too
```

**Scripts must live inside the skill folder.** Pointing outside
(`../../somewhere/x.py`) is refused at declaration time.

The reason is the sandbox. Scripts run isolated, and **the only folder that
environment opens is this skill's own.** A file outside it will not open even
with a correct path, so a declaration pointing outside is a declaration that
could never run. Rather than let it fail strangely at run time, it is **rejected
when declared.**

Put it another way: **a skill must be complete inside its own folder.** Data
files, templates and config the script reads belong there too - that is what
`sample.txt` is doing above.

If you genuinely need a file outside, there is a way: `grant_ro` (a fixed path
always needed) and `grant_args` (a path the caller passes in), both in section 4.

> This document uses **`sample-echo`** throughout. It echoes back the arguments
> it received, so you can see exactly what is passed, and it **ships with the
> node**, so the commands here can be copied and run as-is (section 9).

---

## 4. The full frontmatter

```yaml
---
# identity
name: sample-echo                  # required
description: Echo back arguments.  # the model's only basis for choosing it
version: 0.1.0
author: alice
license: MIT
min_isann: 0.1.0

# search and composition
tags: [echo, arguments, args, params, parameters, verify,
       check, test, diagnostic, sample, example]
tools: [bash]                      # tools this skill uses
skills: [other-skill]              # other skills that must come along
requires: [python]                 # missing -> this skill is not injected

# execution conditions
run: sandbox                       # sandbox (default) | host
net: none                          # none (default) | host
grant_ro: [C:\shared\refdata]      # outside path always needed, read-only
grant_rw: []
grant_args:
  ro: [args]                       # opens a path that arrived as an argument

# calling
scripts:
  echo:
    entry: scripts/echo.py
    params:
      - { name: text, type: string, required: true }
endpoint: local                    # where it runs
---
```

| Field | Meaning |
|---|---|
| `name` | display name, and the name used to call it |
| `description` | **the model's only basis for choosing this skill.** Take your time |
| `tags` | search terms, also used by loadout rules. **Ten or more, with synonyms** |
| `tools` | declared tools **come along with injection.** No permission is granted |
| `requires` | missing on the node and **injection is withheld** |
| `run` | `host` leaves isolation; the operator must grant it separately |
| `net` | `host` when the script needs the network |
| `grant_ro` / `grant_rw` | outside paths **always** needed |
| `grant_args` | opens a path that **arrived as an argument** |

### `tags:` are search terms

Ten or more, **two or three synonyms per concept.** How and why is in
[Overview section 4.6](overview.md).

```yaml
tags: [csv, spreadsheet, excel, table, tabular,
       data, analyze, analysis, statistics, stats,
       summary, rows, columns]
```

`description` is searched too. Put there what tags cannot carry.

### `tools:` brings tools along but grants nothing

Two things happen, and confusing them is a mistake.

| What happens | What does not |
|---|---|
| while this skill is active, **the declared tools are injected too** | those tools are **not made runnable** |
| so you need not list every tool in the loadout | it does not **define** a tool either |

The first is the practical win: turn on one CSV skill and the tools it uses come
with it. That is what `(N via skill)` means in a run trace (section 9).

The second is the safety property. **A declaration is intent, not permission.**
Installing someone else's skill does not make the tools it names suddenly
runnable; the operator grants execution separately by policy.

### `requires:` hides a skill that could not run

List the runtimes the scripts need. If the node lacks one, the skill is **not
injected**:

```
skipped  alice/pdf-tools: missing runtime "python3"
```

On a node without python, **the model never learns the skill exists.**

**Why hide it:** a visible skill that cannot run gets tried, fails, and then the
model **invents a reason for the failure** - "the file seems corrupted" - which
is plausible, wrong, and hides the real cause from everyone.

Withheld skills are **reported with their reason**, not dropped silently. The
line above is that report; the operator installs the runtime and moves on.

> `requires` only ever **removes** capability. Nothing you write there grants
> anything.

### `run:` and `net:` are isolation levels

Scripts run **isolated, with no network**, by default.

| Field | Default | Other | Meaning |
|---|---|---|---|
| `run` | `sandbox` | `host` | run directly on the node, unisolated |
| `net` | `none` | `host` | allow network |

**Use `net: host` when you need it.** A script that fetches packages or calls an
API can do nothing without it.

**`run: host` is different.** It leaves isolation entirely, so the script
reaches everything on the node. Writing it in `SKILL.md` is not enough - **the
operator must grant it separately**, and without that the request is refused.

> Prefer `sandbox`. Needing `host` usually means **folder access is missing**,
> and that is often solved by `grant_*` below.

### `grant_ro`, `grant_rw`, `grant_args` open folders

The sandbox opens **only the skill folder**. Anything outside stays shut even
with a correct path. To reach outside you must say which folder in advance, and
there are two ways.

**1. Fixed paths: `grant_ro` / `grant_rw`**

For a location that is **always the same** - shared reference data, a
dictionary, templates.

```yaml
grant_ro: [C:\shared\refdata]     # read only
grant_rw: [C:\work\output]        # read and write
```

**2. Caller-supplied paths: `grant_args`**

For when **the author cannot know which file will arrive** - every "read this
file for me" case.

```yaml
grant_args:
  ro: [args]      # opens the path that arrived as an argument, read-only
```

Without this, an absolute path **still will not open.** For any skill that
handles user files it is effectively required.

| | When |
|---|---|
| `grant_ro` / `grant_rw` | the path is **fixed** |
| `grant_args` | the **caller** decides the path |

> Keep all three as narrow as the skill can work with. Granting `grant_rw` where
> read-only would do means one bug in the script can wreck that folder.

---

## 5. Writing the body: the model is the reader

The body is not a manual for a person. It is **an instruction sheet for a
model.** Write it from that angle.

**Bad - it never says what to do**

```markdown
# Sample Echo

This skill is very useful. It was built to help users understand
how things work. It supports many options.
```

Not one line about what, when, or how. There is nothing the model can act on.

**Good - when, how, and what comes out**

```markdown
# Sample Echo

Prints back the arguments it received, one per line. Useful for
checking that a call was built the way you meant it.

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

## Output

    echo got 2 argument(s)
      1: hello
      2: 3
    hello
    hello
    hello
```

Three sections have to be there:

| | Why |
|---|---|
| **When to use** | the model decides whether to reach for this skill |
| **How to run it** | it copies the call shape verbatim |
| **Output** | it knows how to read the result |

### Have it write the name, not the ID

```
good:  - `skill`: sample-echo
bad:   - `skill`: 7141c1a9e88f0d2b4c...
```

An ID is a hash of the file contents, and **models struggle to transcribe it.**
One observed run poured out thousands of tokens of hex trying to copy a 64-char
hash and never finished. **Use the name and the node substitutes the ID for
you.**

---

## 6. `scripts:` - making it callable from outside

### 6.1 Why a name instead of a command

There are two ways to run a script:

```jsonc
// A. a command string: the caller composes a sentence
{ "cmd": "python scripts/echo.py hello" }

// B. a declared name: the caller picks from what the author published
{ "script": "echo", "args": ["hello"] }
```

`scripts:` is the declaration that makes B possible, and **calling from outside
requires B.**

#### The set is closed

`scripts:` is a **lookup table.**

```yaml
scripts:
  echo:  scripts/echo.py
  plain: scripts/plain.py
```

```
"echo"                    -> scripts/echo.py       in the table
"plain"                   -> scripts/plain.py      in the table
"cleanup"                 -> (nothing)
"scripts/echo.py"         -> (nothing)
"../../conf/settings"     -> (nothing)
"echo; rm -rf /"          -> (nothing)
```

The last four are **not blocked - they simply do not resolve.** There is no key
like that. There is no separate code guarding against directory escape; **there
is nowhere to express an escape.**

#### Defending versus interpreting

That is the real difference between A and B.

| | The question you must answer | Can it be settled |
|---|---|---|
| **A. command string** | "is this sentence safe?" | no - it never ends |
| **B. name** | "is this key in the table?" | yes - one comparison |

Making A safe means accounting for quoting, chaining (`;` `&&` `|`), command
substitution, redirection, encodings, and every shell's own grammar - **all of
it.** Miss one and it is through. And there is no way to prove you missed none.

B is a string comparison. **Wrong means it does not resolve. That is the end of
it.**

> A command string is something you must **defend against.** A name simply is
> not interpreted.

#### Which is why there is no shell

Even after the name resolves to a file, no shell is involved. The interpreter,
the script and each argument are passed **separately.**

```
script: "echo"
args:   ["; rm -rf /", "$(whoami)", "a|b"]

        |
        v  no shell, verbatim

   python  scripts/echo.py  "; rm -rf /"  "$(whoami)"  "a|b"
                            ^^^^^^^^^^^^  ^^^^^^^^^^^  ^^^^^
                            three separate values
```

```python
sys.argv[1]   # '; rm -rf /'      not executed. Just a string
sys.argv[2]   # '$(whoami)'       not substituted
sys.argv[3]   # 'a|b'             not a pipe
```

**With no shell to interpret, there is nowhere for interpretation to happen.**
No escaping values, no counting quotes.

#### A name can cross the network

This is the premise of a sellable skill.

```
sending a command string to someone's node  =  handing them your shell
sending a name to someone's node            =  asking them to look it up
```

Since **an undeclared name simply does not resolve on the receiving side**, the
sender does not have to be trusted. That is why a skill whose `endpoint` is
another node **accepts only the `script` form and refuses `cmd`:**

```
skill "x" runs on another node, so `cmd` cannot reach it -
call it by declared script name instead (declares: echo, plain)
```

#### And the errors get kinder

A closed set means the node **can say what does exist:**

```
skill "sample-echo" declares no script named "cleanup"
(it declares: echo, plain)
```

A model that guessed wrong picks from the list next turn instead of guessing
again. With an open command string you could not even say what was wrong.

### 6.2 Short form

```yaml
scripts:
  echo:  scripts/echo.py
  plain: scripts/plain.py
```

Name and file only. **Often this is enough** - it makes the script callable by
name and does nothing more.

The cost is that it **knows nothing about arguments.** How many, what type -
none of it is written down, so there is nothing to check against, and a caller
omitting an argument passes straight through to the script, which then dies in
its own way.

Fine for scripts that take no arguments, or where the script's own error is
good enough.

### 6.3 Long form: declare the arguments

```yaml
scripts:
  echo:
    entry: scripts/echo.py             # required
    params:                            # optional
      - name: text
        type: string
        required: true
        description: the text to print
      - name: times
        type: number
        description: how many times to repeat it
```

**Mixing is fine.** The short form is exactly `{entry: <path>}`.

```yaml
scripts:
  echo:                                # declares arguments
    entry: scripts/echo.py
    params: [ { name: text, required: true } ]
  plain: scripts/plain.py              # declares none
```

### 6.4 The order IS the argv order

```
params:  text,      times
args:    ["hello",  "3"]
             |        |
argv:  echo.py    hello    3
```

Arguments arrive as a **positional array**, so something has to say which slot
carries which name. That is why it is a **list**, not a map.

### 6.5 Optional arguments go last

An array cannot skip a middle element - the same constraint a command line has.

```yaml
# good: required first, optional after
params:
  - { name: text, required: true }
  - { name: times }

# bad: optional first
params:
  - { name: times }
  - { name: text, required: true }
```

With the bad version `text` sits in slot two, so **you must send both** even
when you never wanted `times`.

### 6.6 There are only three types

| Value | What it checks | Passes | Rejected |
|---|---|---|---|
| `string` (default) | nothing | everything | nothing |
| `number` | does it read as a number | `3`, `-1.5`, `0` | `abc`, `3 items`, empty |
| `boolean` | does it read as true/false | `true`, `false`, `1`, `0` | `yes`, `on` |

**Only three** because these are the values that fit into one command-line slot
**without ambiguity.** Dates and lists have several notations, so putting one in
a slot immediately splits the interpretation. Put those in a file and pass the
path.

**Every value arrives from the wire as a string.** The model may think it sent
`3`, but `"3"` is what comes. So the check is not "is this of numeric type" but
**"does this text read as a number":**

```
"3"     -> number, passes  (reads as 3)
"-1.5"  -> number, passes
"abc"   -> number, rejected
```

Rejecting `"3"` would break every legitimate call, so this reading is the only
one that makes sense.

> No `type` means `string`, i.e. **no checking.** Where a number is expected,
> write `number`.

### 6.7 What declaring buys you

**A wrong call is rejected before the script starts.**

```
script "echo" requires 1 argument(s) (text), got 0
script "echo": argument 2 (times) must be a number, got "abc"
script "echo" takes at most 2 argument(s) (text, times), got 3
```

Without a declaration it ends like this instead:

```
skill sample-echo failed (exit 1): Traceback (most recent call last):
  File ".../echo.py", line 5, in <module>
    text = sys.argv[1]
IndexError: list index out of range
```

**The difference is large.** The model reads the first kind and fixes itself
next turn, because it is told by name what was missing. The second is Python's
internal business; the model has no idea what to change.

There is a second benefit: **declarations appear in the sale catalog**, so
someone who never read your prose still knows what to send.

```
NAME         SCRIPTS
sample-echo  echo(text, [times]) plain
```

Square brackets mark optional arguments.

### 6.8 The script's own code does not change

Declaring `params` does not change **how the script receives arguments.** They
arrive as ordinary command-line arguments.

```python
import sys

text = sys.argv[1]
times = int(float(sys.argv[2])) if len(sys.argv) > 2 else 1
```

Two things to remember:

**1. The order is exactly what you wrote in `params`.** The first one listed is
`sys.argv[1]`.

**2. Values are strings.** Even declared `type: number`, the script receives the
text `"3"`. Convert it yourself. The example uses `int(float(...))` because both
`"3"` and `"3.0"` can arrive.

**You do not have to check that required arguments are present** - without them
the script never starts. Only optional ones need a `len(sys.argv)` check.

### 6.9 Things that are wrong

```yaml
# points outside the folder
scripts:
  bad: ../../conf/settings.json
```

It must be **inside the skill folder** (section 3). The sandbox will not open outside,
so even if it ran it could not read.

```yaml
# a path where a name belongs
scripts:
  scripts/echo.py: scripts/echo.py
```

The left side is **the name a caller picks**, not a file. Written this way the
caller must type `"scripts/echo.py"`, which looks like a path and **teaches them
that paths are acceptable.** Use a short, clear verb.

```yaml
# invented fields
scripts:
  echo:
    entry: scripts/echo.py
    args: [text, times]            # no such field
    types: { text: string }        # no such field either
```

Writing names and types **separately lets them drift.** A typo in `args` leaves
`types` looking fine, so nobody catches it. That is why only the one-line form
exists:

```yaml
# name, type and required on one line; order is list order
scripts:
  echo:
    entry: scripts/echo.py
    params:
      - { name: text, type: string, required: true }
      - { name: times, type: number }
```

---

## 7. `endpoint:` - deciding where it runs

### 7.1 Why the field exists

Every skill so far ran **on its own node**. Omit `endpoint` and that continues,
so if you are working alone you can skip this section.

> This section is about **how to write the field.** What actually happens on the
> wire - what travels, who is in the middle, whose rules apply - is in
> [Overview section 2](overview.md).

The field exists because of **selling a skill.**

**A purchased skill installs without its scripts.** What the seller distributes
is a single `SKILL.md`; the real implementation in `scripts/` stays on the
seller's node. That is the business model.

So the buyer's disk holds **only a file saying "this can be done"** - with no
code to do it.

```
seller node                      buyer node
  SKILL.md    --- distributed --->  SKILL.md      (the manual only)
  scripts/    --- never sent --X    (absent)
```

When the buyer calls that skill, where should it go? **`endpoint` is the
answer.**

```
endpoint is this node       -> run in my sandbox
endpoint is another node    -> the call goes there (only arguments cross)
```

The same file means **local execution on the seller's node** and a **remote call
on the buyer's**. One file behaves differently depending on who reads it, which
is what lets both copies stay **byte-identical.**

### 7.2 What you can write

```yaml
endpoint: local                   # this node, explicitly
endpoint: this                    # the node reading the file; same as local
endpoint: 0xB1c4...               # a specific node ID
endpoints: [0xB1c4..., 0x77a2...] # one seller's several machines
(omitted)                         # same as local
```

**`endpoint` and `endpoints` are exactly the same field.** Both accept a single
value or an array, and using both merges them. Two names purely for readability.

### 7.3 The value is a node ID, not a URL

```yaml
endpoint: 0xB1c4...                      # "send it to Bob"        good
endpoint: https://bob.example.com/run    # "send it to this address"  refused
```

**A node ID is "who". A URL is "where".** They look similar, but when the other
party changes the outcomes are opposite.

#### A URL does not tell you who is sitting there

| Who | How |
|---|---|
| DNS | the domain can be pointed elsewhere |
| the domain owner | on expiry **anyone can re-register it** |
| a proxy or CDN | can answer instead of reaching the seller |
| a corporate or public network | can intercept the same name |

**The problem is that this is silent.** The response looks normal, so the buyer
has no way to tell.

```
yesterday  https://bob.example.com/run  ->  Bob        result fine
today      https://bob.example.com/run  ->  a stranger  result looks fine too
                                             ^
                     your arguments go there, and so does your money
```

#### A node ID cannot be taken over that way

A node ID is a **wallet address.** A call travels like a **sealed letter with
the recipient written on it.**

1. The buyer writes the note, naming the node it is for.
2. They **stamp it with their private key** and send both.
3. The receiving node **does not simply believe the note.** It rewrites the same
   note **with its own name** and compares.

```
Bob receives it
   rewritten   "to Bob (0xB1c4...)"
   received    "to Bob (0xB1c4...)"      same       -> run

a stranger receives it
   rewritten   "to me (0x99ff...)"
   received    "to Bob (0xB1c4...)"      different  -> refuse
```

A stranger node **works out for itself that this is not for it.**

Editing the name to their own does not help: **the stamp covers the contents**,
so changing them breaks it. Re-stamping needs the **buyer's private key**, which
never leaves the buyer's machine.

> A stranger node has no move: leave it and it is not theirs; change it and the
> stamp breaks. Failing loudly beats running quietly in the wrong place.

The same mechanism blocks **replay**: because the recipient is written into the
note, a paid call cannot be intercepted and re-used against a different node.

#### It suits the seller too

An ID is not a location, so **it survives the seller moving.**

| Situation | With a URL | With a node ID |
|---|---|---|
| change ISP | the address changes; every buyer's file is wrong | unchanged |
| move behind NAT | unreachable from outside | unchanged (the connection is punched through) |
| desktop to laptop | the address changes | unchanged |

"Where it is" is looked up per call, which is why the ID alone is enough.

#### Not yet: proof about the result

The comparison above stops **your call running on the wrong node.** It is not
yet **proof that the result came from that seller** - selling nodes do not sign
their responses.

| | |
|---|---|
| someone else's node running your call | prevented |
| proving where a result came from | not yet |

Once payment is attached a **receipt** becomes necessary - "I paid and got this
result" has to be provable for disputes and reputation to work. Response signing
lands then.

### 7.4 Several machines means "one seller, several counters"

```yaml
endpoints:
  - 0xB1c4...    # desktop
  - 0x77a2...    # laptop
```

**Same product, same owner, several counters.** That is the *only* use for a
list.

It is for one person selling the same skill from a desktop and a laptop, or
spreading load so selling continues when one machine is off. Put the **same
`SKILL.md`** on both and list both.

**It is not for other people's nodes.** If someone else sells something similar,
their `SKILL.md` differs - and different contents mean a **different ID and a
different skill**. Which one to buy is the buyer's choice, not something this
field can merge.

| | |
|---|---|
| each of the seller's nodes | **finds itself** in the list, so runs locally |
| the buyer | finds itself nowhere, so **calls outward** |
| how one is chosen | **at random**, falling through to the others if a connection fails |

**Order is not priority.** Listing one first does not make it preferred. The
choice is random each time so load spreads; reading order as priority would keep
the first node working while the rest idle.

**Only a failed connection moves on to the next node.** If a node answered and
the answer was a failure - not for sale, no such script, the script errored -
**that is the result.** Asking a sibling gets the same answer and spends another
paid call.

> **This assumes calls are stateless.** Any call may land on a different node, so
> a skill that remembers a previous call breaks. Share the state between nodes,
> or design without it.

### 7.5 To sell, your own node must be in there

```yaml
# cannot be sold
endpoint: local        # on a buyer's disk this means "the buyer"
endpoint: this         # every reader becomes itself
endpoint: 0x<someone else>   # buyers' calls arrive at a door that never agreed
(omitted)              # same as local

# good
endpoint: 0x<my node>
endpoints: [0x<my node 1>, 0x<my node 2>]
```

`SKILL.md` reaches the buyer **byte for byte**, which means this one line
**decides execution on their side.**

| Written | On the buyer's node |
|---|---|
| omitted, `local`, `this` | tries their own disk; no scripts, so it fails, and the seller never sees the call |
| someone else's node ID | calls pile up on a node that never agreed to sell |
| **your node ID** | buyers arrive here, and you run locally with no network |

```bash
isann info --proj node_id
```

---

## 8. Editing the file changes the ID

```
ID = sha256(SKILL.md)
```

Not a number assigned from the name or version - a value computed from the
contents. Fix a typo, delete a comment line, and **the ID differs.**

Normally this never matters; you call by name and the node resolves it. **Two
cases bite:**

**1. You edited a skill that was listed for sale.** The listing holds the ID as
it was, which now points at nothing:

```
NAME                       PRICE  SKILL ID
(MISSING - not installed)  free   7141c1a9...
```

**It is not selling.** Re-register the new ID and take the old entry down:

```bash
isann skill ls
isann skill price <new name or ID> --free
isann skill price <old ID> --unlist
```

**2. You keep the same skill on two nodes.** For multi-machine selling (section 7.4)
both copies must be **identical to the byte** or the IDs differ. Copy one file
rather than editing both.

### Why it works this way

**It protects the buyer.** They read a manual and pay. If the seller could later
swap that manual for something that runs differently, the transaction was never
sound.

Binding the ID to the contents makes that structurally impossible. The moment
the seller changes anything, **the ID changes and calls with the old ID simply
do not resolve.**

```
quietly runs something else   <- the worst outcome
just fails                    <- what was chosen
```

The cost is what you are feeling: **edit the manual and you re-register.**

> So settle `endpoint` and `scripts` **before** listing, and one edit is enough.
> Do it the other way round and you register twice.

---

## 9. Running it

### 9.1 The example: `sample-echo`

It ships with the node - no need to build it.

```bash
isann skill list
```
```
#  ID            NAME           VERSION  TOOLS  SRC  LOADOUTS
4  bbd0ff47699a  sample-echo    0.1.0    1      -    -
```

It echoes back whatever it received, so what is passed is visible. It also holds
a **declared** script (`echo`) and an **undeclared** one (`plain`) in the same
skill, so the difference is directly comparable. Use it as a skeleton.

```
skills/sample-echo/
  SKILL.md
  scripts/echo.py
  scripts/plain.py
```

`scripts/echo.py`:

```python
import sys

args = sys.argv[1:]
print("echo got %d argument(s)" % len(args))
for i, a in enumerate(args, 1):
    print("  %d: %s" % (i, a))

text = args[0]
times = int(float(args[1])) if len(args) > 1 else 1
for _ in range(times):
    print(text)
```

> This example reads no files, so it has no `grant_args`. **A skill that takes a
> user's file path as an argument** must open it with `grant_args` (section 4) or it
> cannot read outside its own folder.

### 9.2 Calling it directly

```bash
isann skill ls                          # find the ID; a prefix is enough
isann skill call bbd0ff47 echo hello
```
```
echo got 1 argument(s)
  1: hello
hello
```

Watch the declaration do its work:

```bash
isann skill call bbd0ff47 echo               # missing required argument
isann skill call bbd0ff47 echo hello abc     # type mismatch
isann skill call bbd0ff47 echo hello 3 extra # too many
```
```
bash: script "echo" requires 1 argument(s) (text), got 0
bash: script "echo": argument 2 (times) must be a number, got "abc"
bash: script "echo" takes at most 2 argument(s) (text, times), got 3
```

All three end **before the script starts** - the absence of any `echo got ...`
line is the proof.

**Everything after `<script>` is an argument to the script.** No parsing, no
splitting, no quote handling:

```bash
isann skill call bbd0ff47 plain a b c
isann skill call bbd0ff47 plain "hello there" x
isann skill call bbd0ff47 plain -1.5 --format csv
isann skill call bbd0ff47 plain "; rm -rf /"
```
```
plain got: ['a', 'b', 'c']
plain got: ['hello there', 'x']
plain got: ['-1.5', '--format', 'csv']
plain got: ['; rm -rf /']
```

The only exceptions are this command's own four flags (`--timeout`, `-json`,
`-pretty`, `--proj`), which cannot be passed through as values.

### 9.3 Letting an agent use it

**Creating it does not inject it.** Two routes:

```bash
# A. loadout - always injected
isann loadout add research --includes sample-echo
isann loadout use research
isann agent run "use sample-echo to print hello" --engine llama --trace skills,tools

# B. discovery - surfaces when needed
isann agent run "find a skill that shows how arguments are passed, run it with hello" \
  --engine llama --trace skills,tools
```
```
turn 1  skills   base, search_capabilities
turn 2  skills   base, search_capabilities, sample-echo      <- search surfaced it
        bash {"skill":"sample-echo","script":"echo","args":["hello"]}
```

Route B needs `description` and `tags` to match. Remember the body is English,
so the model has to produce an English query.

### 9.4 Checking what went in

```bash
isann agent run "..." --engine llama --trace skills,tools
```
```
  turn 1
  skills   isann/sample-echo
  tools    search_capabilities, bash  (1 via skill)
```

**The `skills` line** is what entered the system prompt that turn. No name
there and the model does not know the skill exists - either the loadout is not
active, or `requires` withheld it.

**The `tools` line** is what was callable. The trailing `(1 via skill)` counts
the tools **a skill brought along** - what you listed in `tools:`.

> Injected but execution refused is a **permission** problem. A skill bringing a
> tool along is not a grant (section 4); policy decides.
>
> ```bash
> isann policy add --rule execution --tool <tool-ref> user
> ```

---

## 10. Selling

Opening a skill to outside callers is called **listing**, and pricing it and
opening it are **the same action**. Being in the list *is* the permission; there
is nowhere else to grant it.

**Order matters.** Put `endpoint` in first, then list. The other way round the
file changes, the ID changes, and you register twice (section 8).

```bash
isann info --proj node_id          # 1) your node ID
```

Put that in `endpoint`. **Skipping this step gets the listing refused** (section 7.5).

```yaml
endpoint: 0xB1c4...
```

```bash
isann skill price sample-echo --free      # 2) open it, free
isann skill price                         # 3) what am I selling
isann skill price sample-echo --unlist    # 4) take it down
```

**`--unlist` always works**, even for entries that no longer meet the listing
conditions - you must be able to clean up a bad listing without editing files.

> **Paid selling is not wired up yet.** You can set a price, but no payment
> occurs, so priced skills currently run free. Hence only `--free` here.

---

## 11. Common mistakes

| Symptom | Cause | Where |
|---|---|---|
| `non-ASCII byte 0x..` | non-ASCII in the body | make it English/ASCII (section 1) |
| installed but the agent does not know it | not in an active loadout | section 9.3 |
| `skipped: missing runtime "python3"` | `requires:` unmet | install the runtime |
| search does not find it | too few tags, or no synonyms | 10+, 2-3 per concept (section 4) |
| the model cannot transcribe the ID | the body tells it to use an ID | use the **name** (section 5) |
| `declares no script named "x"` | undeclared name | the error lists what exists |
| an argument was omitted and the script died | that script has no `params:` | section 6.3 |
| an argument lands in the wrong slot | `params` order is argv order | section 6.4 |
| cannot skip an optional argument | arrays have no gaps | put optional last (section 6.5) |
| listed but buyers cannot see it | `endpoint` does not name this node | section 7.5 |
| edited it and the listing says `MISSING` | the file changed, so the ID did | re-register (section 8) |
| the script cannot read the user's file | the sandbox opens only the skill folder | `grant_args` / `grant_ro` (section 4) |
| the script has no network | blocked by default | `net: host` (section 4) |
