#!/usr/bin/env bash
# Usage: cat input.ndjson | ./strace_filter_chain.sh filter1.txt filter2.txt ... > output.ndjson

# Start with stdin
cmd="cat"

# For each filter argument, append a python strace_filter stage
for filter_file in "$@"; do
    cmd="$cmd | ./strace_filter.py -f \"$filter_file\""
done

# Execute the constructed pipeline
eval "$cmd"
