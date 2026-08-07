---
name: params-check
description: Analyze a CSV file and echo back the arguments that arrived. Use this to check a CSV, count rows, or verify how script arguments are passed.
version: 0.1.0
author: isann
license: MIT
run: sandbox
net: none
endpoint: local
requires: [python]
tags: [csv, analyze, arguments, params, verification, report]
tools: [bash]
scripts:
  report: scripts/report.py
  analyze:
    entry: scripts/analyze.py
    params:
      - name: csv_path
        type: string
        required: true
        description: path to the CSV file to analyze
      - name: top_n
        type: number
        description: how many rows to show (optional)
---

# Params Check

Analyzes a CSV file. It prints the arguments it received, which makes it useful
for checking that a call was built correctly.

## When to use

Use this skill when the user wants to analyze a CSV file, inspect a spreadsheet,
or check how arguments reach a script.

## How to run it

Run it with the **bash** tool by NAMING the declared script - not by writing a
shell command:

- `skill`: params-check
- `script`: analyze
- `args`: ["sample.csv"]

Write the skill's name, not its id.

`analyze` takes its arguments IN ORDER:

1. `csv_path` (required) - path to the CSV file
2. `top_n` (optional) - a number

So `args` is `["sample.csv"]` or `["sample.csv", "10"]`. The optional one may be
left out, but the required one may not.

## The other script

`report` takes no declared arguments, so anything passed to it is accepted:

- `skill`: params-check
- `script`: report
- `args`: []

## Example

Input:

```
skill: params-check, script: analyze, args: ["sample.csv"]
```

Output:

```
analyze got: ['sample.csv']
```
