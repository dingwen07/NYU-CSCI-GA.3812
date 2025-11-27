#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import re
from strace_parser.parser import get_parser
from strace_parser.json_transformer import to_json

# Regex to strip the <unfinished ...> tag from the start line
# Captures everything BEFORE the tag.
# Example: "123 0.00 read(3, " -> match group 1
RE_UNFINISHED_STRIP = re.compile(r"^(.*)\s+ <unfinished \.\.\.>\s*$", re.DOTALL)

# Regex to extract the tail from the resumed line
# Captures everything AFTER the resumed tag.
# Example: "123 0.00 <... read resumed> \"data\", 10) = 10" -> match group 1 is " \"data\", 10) = 10"
RE_RESUMED_TAIL = re.compile(r"^.*?<\.\.\.\s+\w+\s+resumed>(.*)$", re.DOTALL)

def process_strace_log(filename):
    parser = get_parser()
    
    # State Table: { pid: { "raw_head": "...", "name": "read", "start_timestamp": 123.456 } }
    pending = {}
    
    DEFAULT_PID = 0
    line_num = 0

    with open(filename, 'r') as f:
        for line in f:
            line_num += 1
            original_line = line.strip()
            if not original_line:
                continue

            try:
                # --- Pass 1: Initial Parse to identify type ---
                tree = parser.parse(original_line + '\n')
                event = to_json(tree)
                if isinstance(event, list): event = event[0]

                # Identify PID context
                pid = event.get('pid', DEFAULT_PID)
                status = event.get('status')

                # --- Case 1: Unfinished Start ---
                if status == 'unfinished':
                    # 1. Strip the "<unfinished ...>" tag using Regex
                    match = RE_UNFINISHED_STRIP.match(original_line)
                    if match:
                        raw_head = match.group(1)
                    else:
                        # Fallback if regex fails (unlikely if parser matched UNFINISHED)
                        # Just strip the last 16 chars "<unfinished ...>"
                        raw_head = original_line.replace("<unfinished ...>", "").rstrip()

                    # 2. Store in memory
                    pending[pid] = {
                        "raw_head": raw_head,
                        "name": event.get("name"),
                        "start_timestamp": event.get("timestamp")
                    }

                # --- Case 2: Resumed End ---
                elif status == 'resumed':
                    if pid not in pending:
                        print(f"Error Line {line_num}: PID {pid} resumed without unfinished start.", file=sys.stderr)
                        continue

                    start_ctx = pending.pop(pid)

                    # 1. Validation: Syscall names must match
                    if event.get("name") and start_ctx["name"] != event.get("name"):
                         # Note: sometimes strace resumed tag doesn't have name if ambiguous, 
                         # but usually it does.
                         print(f"Error Line {line_num}: Mismatch name. Started {start_ctx['name']}, Resumed {event.get('name')}", file=sys.stderr)
                         continue

                    # 2. Extract the tail (args/result) from resumed line
                    tail_match = RE_RESUMED_TAIL.match(original_line)
                    if not tail_match:
                        print(f"Error Line {line_num}: Could not parse resumed tail regex.", file=sys.stderr)
                        continue
                    
                    raw_tail = tail_match.group(1)

                    # 3. Stitch lines together
                    # Head: "51302 176424... close(255"
                    # Tail: ") = 0"
                    reconstructed_line = start_ctx["raw_head"] + raw_tail

                    # 4. RE-PARSE the reconstructed line
                    # This is the "magic" step. The parser now sees a perfect, complete syscall.
                    new_tree = parser.parse(reconstructed_line + '\n')
                    new_event = to_json(new_tree)
                    if isinstance(new_event, list): new_event = new_event[0]

                    # 5. Add Metadata from the Resumed event
                    # We keep the start timestamp from the reconstructed line (which came from head)
                    # We add the end timestamp from the current resumed line
                    new_event['end_timestamp'] = event.get('timestamp')
                    
                    if 'status' in new_event:
                        del new_event['status']
                    print(json.dumps(new_event))

                # --- Case 3: Standard (Atomic) Lines ---
                else:
                    if 'status' in event:
                        del event['status']
                    print(json.dumps(event))

            except Exception as e:
                print(f"Error processing line {line_num}: {e}", file=sys.stderr)
                print(f"Line: {original_line}", file=sys.stderr)
                break

if __name__ == "__main__":
    log_file = None
    if len(sys.argv) > 3:
        print("Usage: python strace_analyzer.py <strace_log_file>")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        log_file = sys.argv[1]
        if not os.path.isfile(log_file):
            print(f"Error: File '{log_file}' does not exist.")
            sys.exit(1)
    else:
        log_file = sys.stdin.fileno()

    process_strace_log(log_file)
