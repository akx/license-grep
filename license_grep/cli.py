import argparse
import json
import sys

from license_grep.js import process_js_environment
from license_grep.output import write_json, write_license_table, write_grouped_markdown
from license_grep.python import process_python_environment
from license_grep.utils import strip_versions


def read_data_from_env(directory):
    data = {}
    process_js_environment(data, directory)

    print("Processing Python environment")
    process_python_environment(data)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--directory", default=".")
    ap.add_argument("-r", "--read-json", required=False, type=argparse.FileType("r"))
    ap.add_argument("-w", "--write-json", required=False, type=argparse.FileType("w"))
    ap.add_argument("-t", "--write-table", required=False, type=argparse.FileType("w"))
    ap.add_argument(
        "-g", "--write-grouped-markdown", required=False, type=argparse.FileType("w")
    )
    ap.add_argument("-s", "--strip-versions", default=False, action="store_true")
    args = ap.parse_args()
    if args.read_json:
        data = json.load(args.read_json)
    else:
        data = read_data_from_env(args.directory)

    print(f"{len(data):d} packages found.", file=sys.stderr)

    if args.strip_versions:
        data = strip_versions(data)
        print(f"{len(data):d} packages after stripping versions.", file=sys.stderr)

    for spec, package in data.items():
        package['spec'] = spec

    if args.write_json:
        write_json(data, fp=args.write_json)
        print(f"JSON written to {args.write_json.name}", file=sys.stderr)

    if args.write_table:
        write_license_table(data, fp=args.write_table)
        print(f"Markdown table written to {args.write_table.name}", file=sys.stderr)

    if args.write_grouped_markdown:
        write_grouped_markdown(data, fp=args.write_grouped_markdown)
        print(
            f"Markdown written to {args.write_grouped_markdown.name}", file=sys.stderr
        )
