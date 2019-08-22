import argparse
import json
import sys

from license_grep.js import process_js_environment
from license_grep.python import process_python_environment


def read_data_from_env():
    data = {}
    process_js_environment(data)

    print("Processing Python environment")
    process_python_environment(data)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--read-json", required=False, type=argparse.FileType("r"))
    ap.add_argument("-w", "--write-json", required=False, type=argparse.FileType("w"))
    ap.add_argument("-t", "--write-table", required=False, type=argparse.FileType("w"))
    ap.add_argument("-s", "--strip-versions", default=False, action="store_true")
    args = ap.parse_args()
    if args.read_json:
        data = json.load(args.read_json)
    else:
        data = read_data_from_env()

    print("%d packages found." % len(data), file=sys.stderr)
    if args.strip_versions:
        data = strip_versions(data)
        print("%d packages after stripping versions." % len(data), file=sys.stderr)

    if args.write_json:
        write_json(data, fp=args.write_json)
        print("JSON written to %s" % args.write_json.name, file=sys.stderr)

    if args.write_table:
        write_license_table(data, fp=args.write_table)
        print("Markdown table written to %s" % args.write_table.name, file=sys.stderr)
