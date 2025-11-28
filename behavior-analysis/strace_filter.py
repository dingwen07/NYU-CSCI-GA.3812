#!/usr/bin/env python3

import os
import sys
import json
import argparse
import re

from typing import List, Tuple

from jsonpath_rw_ext import parse as jsonpath_parse

FILTER_LINE_SEPARATOR = ':::'

def parse_filter_file(filter_filename) -> Tuple[bool, List[Tuple[str, str]]]:
    include_mode = True
    filters = []
    with open(filter_filename, 'r') as f:
        lines = f.readlines()
        if not lines:
            raise ValueError("Filter file is empty.")
        
        first_line = lines[0].strip().lower()
        if first_line == 'include':
            include_mode = True
        elif first_line == 'exclude':
            include_mode = False
        else:
            raise ValueError("Invalid Filter: first line must be 'include' or 'exclude'.")
        
        for line in lines[1:]:
            line = line.strip()
            # split by # and //
            line = line.split('#', 1)[0].split('//', 1)[0].strip()
            if line:
                parts = line.split(FILTER_LINE_SEPARATOR, 1)
                filters.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else None))

    
    return include_mode, filters

def entry_matches(entry: dict, filters) -> bool:
    for filter in filters:
        jsonpath_expr = filter[0]
        regex = filter[1]
        matches = jsonpath_expr.find([entry])
        if matches:
            if regex:
                # Additional regex match
                for match in matches:
                    if re.search(regex, str(match.value)):
                        return True
            else:
                return True
                        
    return False

if __name__ == "__main__":
    # Usage: python strace_filter.py --filter/-f <filter_file> [input_file] (or -i input_file or none for stdin) --output/-o <output_file> (or none for stdout)
    parser = argparse.ArgumentParser(description="Filter strace JSON log based on JSONPath expressions.")
    parser.add_argument('-f', '--filter', required=True, help="Path to filter file containing JSONPath expressions, one per line. First line specifys inclusion/exclusion.")
    parser.add_argument('-i', '--input', help="Input strace JSON log file. If not provided, reads from stdin.")
    parser.add_argument('-o', '--output', help="Output file for filtered log. If not provided, writes to stdout.")
    parser.add_argument('positional_input', nargs='?', help="Positional input file (shorthand for -i).")
    args = parser.parse_args()
    filter_file = args.filter
    input_file = args.input if args.input else args.positional_input
    output_file = args.output
    include_mode, filters = parse_filter_file(filter_file)
    jsonpath_exprs = [jsonpath_parse(f[0]) for f in filters]
    regexes = [f[1] for f in filters]

    input_stream = open(input_file, 'r') if input_file else sys.stdin
    output_stream = open(output_file, 'w') if output_file else sys.stdout
    with input_stream, output_stream:
        for line in input_stream:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error decoding JSON line: {line}", file=sys.stderr)
                continue
            
            matches = entry_matches(entry, zip(jsonpath_exprs, regexes))
            if (include_mode and matches) or (not include_mode and not matches):
                output_stream.write(line + '\n')
