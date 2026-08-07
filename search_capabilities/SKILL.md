---
name: search_capabilities
description: Find and use tools and skills that aren't already in front of you. Apply this whenever a task needs a capability you don't see - search for it first, then call it.
version: 0.1.0
min_isann: 0.1.20
author: isann
license: MIT
endpoint: local
tools:
  - search_capabilities
  - read_capability
tags: [core, discovery]
---

# Tool Discovery

Only a lean set of tools is shown to you up front. This node exposes many more -
reach them by searching instead of giving up or describing what could be done.

## When to use

Whenever you need to do something and you do NOT see a tool for it. Do not tell
the user to run a command themselves and do not ask permission - find the tool.

## How

1. Call **search_capabilities** with a short, plain-language capability query - words
   for the task, not a tool name. **Write the query in English**, whatever language
   you are answering in: every asset is indexed by its English name, tags, and
   description, so a query in another language comes back empty. Translate the
   user's request into an English capability phrase first. Examples:

   ```
   search_capabilities{ query: "restart an engine" }
   search_capabilities{ query: "this node id and hardware" }
   search_capabilities{ query: "list running containers" }
   ```

2. It returns the best matches, each with a `kind`:
   - `kind: "tool"` - has `name`, `description`, `parameters` (the call schema)
   - `kind: "skill"` - has `name`, `id`, `description`. **No know-how text here.**

3. For a **tool**, call it directly by its `name`, filling the arguments from the
   `parameters` schema it returned. The search gave you everything you need.

4. For a **skill**, you got only a pointer. Call **read_capability** with that
   result's `id` to get the skill's full instructions:

   ```
   read_capability{ id: "the id the search result gave you" }
   ```

   The result's `body` is the skill's know-how - what it does, the exact command to
   run, and its arguments. **Read it before acting.** Do not guess the steps from
   the one-line description; a skill exists precisely because the description is
   not enough.

   If the skill bundles a script, run the command its body names with the **bash**
   tool, passing that same **`id`** as bash's `skill` argument - copied exactly,
   with no quotes or brackets. A skill is addressed by id, never by name.

5. **Once a search returns something that fits, STOP SEARCHING AND CALL IT.** The
   results are ranked; the top hit is usually the answer. Searching the same need
   from another angle does not improve on it - it spends the turn and pushes the
   result you already had out of view. Only search again if the results contained
   nothing usable, and then change the WORDS, not the number of tries.

   You may make **at most 3** searches/reads in one turn. Past that the node
   refuses them and tells you to act on what you have.

6. Do not read a skill that is already in the **Skills** section of your system
   prompt - its full text is in front of you, and reading it returns nothing new.
   `read_capability` is for a skill a search just pointed you at.

## Notes

- Finding a tool does not grant permission to run it. If a returned tool needs a
  tier or an execution grant you lack, it will say so when you call it - report
  that to the user rather than retrying blindly.
- One focused query beats several broad ones. A turn spent only looking is a turn
  with no work in it.
