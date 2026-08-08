import os
import sys

path = sys.argv[1]
limit = int(float(sys.argv[2])) if len(sys.argv) > 2 else 0

if not os.path.exists(path):
    print("file not found: %s" % path)
    sys.exit(1)
if os.path.isdir(path):
    print("that is a folder, not a file: %s" % path)
    sys.exit(1)

with open(path, encoding="utf-8", errors="replace") as f:
    lines = f.read().splitlines()

print("file  : %s" % path)
print("lines : %d" % len(lines))
print()

shown = lines if limit <= 0 else lines[:limit]
for i, line in enumerate(shown, 1):
    print("%4d | %s" % (i, line))

if 0 < limit < len(lines):
    print("... (%d more)" % (len(lines) - limit))
