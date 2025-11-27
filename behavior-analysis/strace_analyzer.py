#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# strace -ttt -xx -y -ff -s 65535 -o trace.log <cmd>
# strace -ttt -xx -ff -s 65535 -o trace.log <cmd>


import sys
import os
import json
from strace_parser.parser import get_parser
from strace_parser.json_transformer import to_json

if __name__ == "__main__":
    
    # read from arg 1
    if len(sys.argv) < 2:
        print("Usage: python strace_analyzer.py <strace_log_file>")
        sys.exit(1)
    strace_log_file = sys.argv[1]
    if not os.path.isfile(strace_log_file):
        print(f"Error: File '{strace_log_file}' does not exist.")
        sys.exit(1)
    
    # get parser
    parser = get_parser()

    i = 1

    # for each line
    with open(strace_log_file, 'r') as f:
        # for lines
        for line in f:
            print(f"--- Line {i} ---", flush=True, file=sys.stderr)
            line = line.strip()
            if not line:
                continue
            # parse line
            tree = parser.parse(line + '\n')
            i += 1
            # transform to JSON
            try:
                json_data = to_json(tree)
            except Exception as e:
                print(f"Error transforming to JSON: {e}")
                print(tree.pretty())
                break
            try:
                print(json.dumps(json_data[0]))
            except Exception as e:
                print(f"Error dumping JSON: {e}")
                print(json_data)
                break
