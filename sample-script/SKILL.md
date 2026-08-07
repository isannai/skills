---
name: sample-script
description: Analyze a CSV file - report the row count and per-column numeric statistics (mean, min, max). A sample skill showing how a skill bundles a script and runs it through bash.
version: 0.1.0
min_isann: 0.1.0
author: isann
license: MIT
run: sandbox
net: none
endpoint: 0xbada8be86f587f96901a3c8d3492a3b0f13c7cee
requires: [python]
grant_args:
  ro: [args]
tools: [bash]
scripts:
  analyze: scripts/analyze.py
---

# Sample Script

A sample skill: it bundles a small analysis script (`scripts/analyze.py`) and runs
it through the **bash** tool. It summarizes a CSV - the total row count and, for
every purely-numeric column, the mean, minimum, and maximum.

## When to use

Use this skill when the user wants statistics, a row count, or a column summary
from a CSV or spreadsheet file.

## How to run it

Run it with the **bash** tool by NAMING the declared script - not by writing a
shell command:

- `skill`: sample-script
- `script`: analyze
- `args`: ["sample.csv"]

Write the skill's name, not its id. A `cmd` shell string works only while the
skill runs on this machine; a declared name works either way, so this is the one
form to use.

- A bundled `sample.csv` is included for a quick test - use `sample.csv` as the path.
- For a user-supplied file, pass its absolute path; the script reads it read-only.

The script prints the row count and a table of per-column statistics to stdout.

## Example

Input:

```bash
python scripts/analyze.py sample.csv
```

Output:

```
file : sample.csv
rows : 6
cols : 4

column                 count         mean          min          max
-----------------------------------------------------------------
region                     6            (text, 4 uniq)
amount                     6     2235.000      300.000     9800.000
qty                        6        3.667        1.000        7.000
price                      6      469.167      100.000     1400.000
```
