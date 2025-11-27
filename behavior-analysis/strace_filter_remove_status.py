#!/usr/bin/env python3

import sys
import json

if __name__ == '__main__':
    # Usage: python strace_filter_remove_status.py
    # Input only from stdin, output to stdout

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if 'status' in entry:
                del entry['status']
            print(json.dumps(entry))
        except json.JSONDecodeError:
            print(f"Error decoding JSON line: {line}", file=sys.stderr)
            continue
