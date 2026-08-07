import sys

args = sys.argv[1:]
print("echo got %d argument(s)" % len(args))
for i, a in enumerate(args, 1):
    print("  %d: %s" % (i, a))

text = args[0]
times = int(float(args[1])) if len(args) > 1 else 1
for _ in range(times):
    print(text)
