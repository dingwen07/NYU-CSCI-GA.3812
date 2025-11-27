#!/usr/bin/env python3

import sys
import json

FORMAT_STRING = '{PID}\t{TIMESTAMP}\t{SYSCALL}({ARGS})\t= {RETURN}'

if __name__ == '__main__':
    # Usage: python strace_json_flattern.py
    # Input only from stdin, output to stdout

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            pid = entry.get('pid', '')
            timestamp = entry.get('timestamp', '')
            syscall = entry.get('name', '')
            args = json.dumps(entry.get('args', ''))
            ret = json.dumps(entry.get('result', ''))
            flat_line = FORMAT_STRING.format(PID=pid, TIMESTAMP=timestamp, SYSCALL=syscall, ARGS=args, RETURN=ret)
            print(flat_line)
        except json.JSONDecodeError:
            print(f"Error decoding JSON line: {line}", file=sys.stderr)
            continue

            