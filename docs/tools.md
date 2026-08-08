# Writing a Tool

> A **tool is one function the model can call.** It lives in a `tools.json`
> file, which holds both **what the model is shown** and **what actually runs**.

This is the end-to-end guide. For the shared rules - where files live, the ASCII
constraint, how IDs work, injection vs execution permission - see the
[Capabilities Overview](overview.md).

---

## 1. A tool creates a capability

A tool is what lets the node do something it could not do before. The model
calls it like a function.

### One bundle, several tools

A single `tools.json` can declare **several tools**. That group is a **bundle**,
and the folder name is the bundle name.

```
tools/
  weather/
    tools.json      <- several tools can live in here
```

Bundling matters because it is the unit an operator turns on and off. Three
weather tools in one bundle are managed as one thing.

The opposite pressure: the ID is a hash of the file, so with ten tools in one
file, editing one changes all ten IDs. Split bundles that grow.

> **`tools.json` must be printable ASCII.** Not one non-ASCII character.

---

## 2. The smallest tool

Wrapping an outside API is the simplest shape - no container, no binary.

```json
{
  "spec_version": "1",
  "name": "weather",
  "version": "0.1.0",
  "author": "alice",
  "license": "MIT",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "weather_now",
        "description": "Get the current weather for a city. Returns temperature in Celsius and a one-word condition.",
        "parameters": {
          "type": "object",
          "properties": {
            "city": { "type": "string", "description": "city name in English, e.g. Seoul" }
          },
          "required": ["city"]
        },
        "tags": ["weather", "forecast", "temperature", "climate", "city"]
      },
      "execution": {
        "handler": "http",
        "auth": "user",
        "http": {
          "method": "GET",
          "url": "https://api.example.com/weather",
          "query": { "q": "${city}" }
        }
      }
    }
  ]
}
```

Put it here:

```
<install-root>/artifacts/addon/tools/weather/tools.json
```

```bash
isann tool list
```

If it appears, it is in. The node re-reads changed files, so **no restart.**

---

## 3. The file has two layers

Each entry holds **two completely different things.** This distinction is the
most important idea in this document.

```json
{
  "function":  { ... },     // what the model sees
  "execution": { ... }      // what actually happens
}
```

| | `function` | `execution` |
|---|---|---|
| Who reads it | **the model** | the node only |
| What is in it | name, description, argument schema | what to run and how |
| If it is wrong | the model **won't call it, or calls it wrong** | execution **fails** |

**`function` is the advertisement; `execution` is the wiring.** The model never
sees `execution` - not the URL, not the command, not the key. All it knows is
"call this name with these arguments and you get this back".

That separation is also a safety property: **the model cannot choose the
destination.** The author pins where the request goes; the model only fills in
the blanks inside it.

---

## 4. Writing `function`

### 4.1 `description` is everything

It is the **only** basis on which the model picks this tool. There is no body
text. Get this paragraph wrong and the tool may as well not exist.

**Bad**

```json
"description": "Weather API wrapper."
```

Nothing about what goes in, what comes out, or when to use it. The model cannot
decide whether to call it.

**Good**

```json
"description": "Get the CURRENT weather for one city. Returns temperature in Celsius, humidity, and a one-word condition (clear/cloudy/rain/snow). Use this when the user asks what the weather is like right now. It does NOT do forecasts - for tomorrow or later, use weather_forecast instead. City names must be in English."
```

Four things are in there:

| | Why it is needed |
|---|---|
| **What it does** | the basis for choosing it |
| **What comes back** | so the model knows how to read the result |
| **When to use it** | separates it from similar tools |
| **What it cannot do** | stops it being picked for the wrong job |

The fourth matters most. **If you do not say what it cannot do, the model
assumes it can.** Asked for a forecast, it will call the current-weather tool
and then explain the odd result plausibly.

> Length is fine. `description` is not a human summary - it is **the spec you
> hand the model.**

### 4.2 `parameters` is JSON Schema

It is the only thing the model consults when building arguments, and what the
engine enforces **grammatically**.

```json
"parameters": {
  "type": "object",
  "properties": {
    "city":  { "type": "string",  "description": "city name in English, e.g. Seoul" },
    "days":  { "type": "integer", "description": "how many days ahead, 1-7" },
    "units": { "type": "string",  "enum": ["metric", "imperial"],
               "description": "metric (default) or imperial" }
  },
  "required": ["city"]
}
```

**Describe every argument.** The name alone does not say whether `days` starts
at 0 or 1, or whether `city` may be non-English.

**Get `required` right.** What is not listed may be omitted; what is listed will
always be filled.

**Use `enum` whenever the choices are fixed.** The model then cannot invent a
value, and a grammar-constrained engine cannot even generate one.

A tool that takes no arguments still needs the object:

```json
"parameters": { "type": "object", "properties": {} }
```

#### With no required argument, calls come out half-finished

An object with nothing required is **already complete after one key.** A
grammar-constrained engine has every reason to stop there, and it does.

**Keep at least one required argument.** Filling it is what carries the call to
completion. If the shape varies too much to put `required` at the top level, use
`oneOf` below.

### 4.3 `oneOf`: two genuinely different shapes

Sometimes one tool accepts **mutually exclusive** call shapes - "either a
command string, or a declared name plus arguments". Neither is always required,
so top-level `required` cannot express it.

```json
"parameters": {
  "type": "object",
  "properties": {
    "cmd":    { "type": "string", "description": "a shell command" },
    "script": { "type": "string", "description": "a declared script name" },
    "args":   { "type": "array", "items": { "type": "string" } }
  },
  "oneOf": [
    { "title": "cmd",    "required": ["cmd"] },
    { "title": "script", "required": ["script", "args"] }
  ]
}
```

Without it the previous trap reappears: the model writes `{"skill": "x"}` and
stops. One observed run repeated exactly that half-call for eight turns while
correctly *describing* the call it could not emit.

With `oneOf`, whichever branch is chosen, that branch's required fields must be
filled.

#### Always give each branch a `title`

`title` is standard JSON Schema and does not affect validation. What it buys is
**an operator being able to name the branch**:

```bash
# open the script branch, close the cmd branch
isann policy add --rule form --tool <tool> --allow script
```

The `cmd` branch then **disappears from the schema entirely** - not just its
required list, but the properties only that branch used - so the model cannot
produce that shape at all.

| | |
|---|---|
| `title` present | operators can switch branches on and off |
| `title` absent | the branch works but **cannot be controlled by policy** |

> This applies to every tool. The node does not look at tool names, only at
> `oneOf` and `title`.

Declaring branches does not lock them: with no policy, every declared branch is
open. The one exception is `bash`, whose arbitrary-command branch is closed by
default.

### 4.4 `tags` are search terms

Ten or more, **two or three synonyms per concept**. `description` is searched
too, so put in tags what a sentence cannot carry.

```json
"tags": ["weather", "forecast", "temperature", "climate",
         "rain", "snow", "city", "outside", "conditions", "now"]
```

### 4.5 Naming

```
good:  weather_now, weather_forecast, docker_restart
bad:   get, run, do_it, helper
```

**The model reads the name too** - before it reads the description. Sharing a
prefix within a bundle helps it group related tools.

---

## 5. Writing `execution`

### 5.1 Four handlers

| `handler` | What it does | When |
|---|---|---|
| `http` | sends an HTTP request | wrapping an outside API, or a container backend |
| `exec` | runs a program | local computation, file processing |
| `isannd` | node built-ins | **not available to tools you write** |
| `code` | reserved | |

In practice you write `http` and `exec`.

> `isannd` is for functions already compiled into the node (docker control,
> listings, search). Writing it in `tools.json` does not create a built-in.

### 5.2 `auth` is who may call it

```json
"auth": "user"     // read, list, infer
"auth": "admin"    // changes state, control
```

**When in doubt use `admin`.** Loosening later is easy; tightening something
already open is not.

### 5.3 `handler: "http"`

```json
"execution": {
  "handler": "http",
  "auth": "user",
  "http": {
    "method": "GET",
    "url": "https://api.example.com/weather",
    "query":   { "q": "${city}" },
    "headers": { "Authorization": "Bearer SECRET" }
  }
}
```

```json
"execution": {
  "handler": "http",
  "auth": "user",
  "http": {
    "method": "POST",
    "url": "http://127.0.0.1:8500/search",
    "body": { "q": "${query}", "top_k": "${top_k}" }
  }
}
```

A body gets `Content-Type: application/json` automatically. Omit the slots you
do not use rather than leaving them empty.

#### Where you put `${arg}` is where it goes

| Placed in | Ends up as |
|---|---|
| `query` | URL query string |
| `body` | request body |
| `headers` | a header |

The same `${city}` is unambiguous because its position decides.

#### Type is preserved when the placeholder is the whole value

```json
"body": { "top_k": "${top_k}" }        // whole value -> stays a number
"body": { "label": "page ${n}" }       // inside a sentence -> becomes a string
```

Numbers, booleans and objects survive when the placeholder is the entire value.

#### Optional arguments substitute to empty, not away

```json
"query": { "units": "${units}" }
```

If the model omits `units` you get `?units=`, not a removed key. If the server
rejects empty values the request fails. Either make it `required`, or check the
server tolerates the empty form.

#### An argument cannot change the destination

`${}` works inside the URL, but **host:port must stay as written in the
template.** If substitution points elsewhere the request is refused:

```
addon weather.weather_now: refusing request - an argument changed
the target host ("evil.example.com" != template "api.example.com")
```

So even a model taken in by an injected instruction cannot send the request
somewhere else. Path and query are fillable; the destination is pinned.

#### The rest

| | |
|---|---|
| `method` omitted | treated as **POST**. State it anyway |
| 4xx / 5xx | become **errors**, reported to the model as failure |
| Response size | read up to **1 MiB**, then truncated |
| Response body | passed to the model **verbatim** |

That last row matters: **the model reads whatever JSON the API emits.** A large,
chatty response eats context and makes the model wander. Trim it server-side
where you can.

> The model cannot see the URL or headers, so an API key in a header is not
> exposed to it. It does sit in `tools.json` in plain text, though - mind where
> that file lives and who you share it with.

### 5.4 `handler: "exec"`

```json
"execution": {
  "handler": "exec",
  "auth": "user",
  "exec": {
    "command": "python",
    "args": ["scripts/convert.py", "${input_path}", "${format}"],
    "run": "sandbox",
    "net": "none",
    "timeout_sec": 60,
    "grant_args": { "ro": ["input_path"] }
  }
}
```

**There is no shell.** `command` and each element of `args` are passed
separately, so a value containing `;` or `|` is just a string.

| Field | Meaning |
|---|---|
| `command` | the program to run |
| `args` | argument array; `${name}` is substituted |
| `input` | `argv` (default) or `stdin-json` |
| `cwd` | working directory |
| `timeout_sec` | upper bound |
| `run` | `sandbox` (default) or `host` |
| `net` | `none` (default) or `host` |
| `grant_ro` / `grant_rw` | **fixed** paths always needed |
| `grant_args` | opens a path that arrived **as an argument** |

By default it runs isolated with no network, and the only folder open is the
tool's own.

**`grant_args` is the key for touching user files:**

```json
"grant_args": { "ro": ["input_path"] }
```

Only the path that arrived in `input_path` is opened, read-only. The author
decides *which argument* and *read or write*; the caller supplies the path. That
is what keeps a read tool a read tool.

> **`run: "host"` leaves isolation entirely.** Writing it in `tools.json` is not
> enough - the operator must grant it separately. Prefer `sandbox`, and if what
> you need is folder access, open it with `grant_*`.

### 5.5 `x-isann-ref`: when an argument names a skill

If an argument's value points at a skill (or a script inside one), mark it -
inside `function.parameters`:

```json
"skill":  { "type": "string", "x-isann-ref": "skill",  "description": "which skill to run" },
"script": { "type": "string", "x-isann-ref": "script", "description": "a script that skill declared" }
```

One line does two things:

**1. The slot is filled with the values available right now.** Just before the
call the node copies the schema and injects the skill names actually present as
an `enum`, so the model **chooses from a list instead of inventing a value.** A
grammar-constrained engine cannot generate anything outside it. Invented names,
file paths and guesswork disappear.

**2. A name is turned into an ID.** Skill IDs are long hashes that models
mistype. With this marker the model writes the **name** and the node substitutes
the exact ID at call time.

> Any tool can use this. The node looks only at the marker, never at tool names.

`x-` extension fields are ignored by JSON Schema validators and are not visible
to the model as a rule - they are metadata only the node reads.

---

## 6. Running it

```bash
isann tool list
isann tool call weather_now --args "{\"city\":\"Seoul\"}"
isann tool inspect weather
```

`--args` is a JSON string. It skips the model, which makes it the right way to
test the `execution` wiring on its own.

### Letting an agent use it

**Creating a tool does not show it to the model.** Put it in a loadout:

```bash
isann loadout add research --includes weather
isann loadout use research

isann agent run "what is the weather in Seoul?" --engine llama --trace tools
```

Or let it be found: good `tags` and `description` make it discoverable through
`search_capabilities` when the model needs it.

### Execution permission is separate

Being listed and being runnable are different things.

```bash
isann policy add --rule execution --tool <tool-ref> user
```

**`exec` handlers and destructive tools are blocked by default.** If the tool is
visible but the call is refused, this is why.

### Checking what was injected

```bash
isann agent run "..." --engine llama --trace tools
```
```
  turn 1
  tools    search_capabilities, weather_now, bash
```

If the name is missing from that line, the model does not know the tool exists.

### Running on another node (P2P)

A tool can run on **another node you operate**. The nodes connect directly - no
server in between.

```bash
isann tool call weather_now --args "{\"city\":\"Seoul\"}" --nodes <node>
```

The output has the same shape as a local run - just the result, not a
node-labelled table - so a command that pipes onward works regardless of where
it ran.

Two limits, both deliberate:

| Limit | Why |
|---|---|
| **one node at a time** | running a tool has side effects; fan out to three and have one fail, and the states diverge in a way the CLI cannot repair for you |
| **`--run` cannot be combined** | running on *your* host is your decision; running on *someone else's* host is that operator's decision |

> `--nodes` goes through the **operator door**: your wallet must be owner or
> admin on that node. It is for your second node or a team node, not a
> stranger's. The only door open to others is a **listed skill**, not a tool.

---

## 7. A tool with a container

When you wrap your own server rather than an outside API, put a
`docker-compose.yml` in the folder:

```
tools/myrag/
  tools.json           <- handler: "http" pointing at localhost
  docker-compose.yml
```

```json
"http": { "method": "POST", "url": "http://127.0.0.1:8500/search",
          "body": { "q": "${query}" } }
```

**The container does not start itself.** The receiving operator brings it up:

```bash
isann docker create myrag
isann docker start myrag
```

That keeps containers from running on someone's machine without consent, with
`docker start` as the human checkpoint.

---

## 8. Editing the file changes the ID

A tool's ID is the hash of `tools.json`. One character changes it.

Normally you call tools by name and never notice - until **a policy points at an
ID**:

```bash
isann policy add --rule execution --tool tool:7141c1a9 user
```

Edit `tools.json` after that and the policy points at nothing. If execution is
suddenly refused, suspect this:

```bash
isann tool list        # the new ID
isann policy list      # rules still naming the old one
```

Smaller bundles reduce the blast radius: ten tools in one file means editing one
changes all ten IDs.

---

## 9. Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `non-ASCII byte 0x..` | non-ASCII in the file | make it English/ASCII (section 1) |
| not listed | broken JSON or wrong folder | `isann tool list` (section 2) |
| listed but never called | not in an active loadout | section 6 |
| in the loadout, still not called | `description` does not say WHEN to use it | section 4.1 |
| the wrong similar tool gets called | you did not say what it **cannot** do | section 4.1 |
| search does not find it | too few `tags` | 10+ (section 4.4) |
| called with empty arguments | nothing is `required` | `required` (section 4.2), `oneOf` if the shape varies (section 4.3) |
| cannot block a dangerous call shape | the `oneOf` branch has no `title` | section 4.3 |
| argument lands in the wrong place | `${name}` in the wrong slot | query/body/headers (section 5.3) |
| a number arrives as a string | placeholder sits inside a sentence | make it the whole value (section 5.3) |
| an empty `?units=` is sent | the model omitted an optional argument | make it `required` (section 5.3) |
| `refusing request - an argument changed the target host` | an argument tried to move the destination | working as intended (section 5.3) |
| response truncated | 1 MiB cap | trim server-side (section 5.3) |
| visible but execution refused | no execution grant | section 6 |
| the script cannot read the user's file | the sandbox opens only the tool folder | `grant_args` (section 5.4) |
| no network | blocked by default | `net: "host"` (section 5.4) |
| something that worked is suddenly refused | the file changed, so the ID did | section 8 |
| cannot reach the container | it was never started | `docker start` (section 7) |
