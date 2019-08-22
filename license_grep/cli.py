import argparse
import sys

from license_grep.input.dart import process_dart_environment
from license_grep.input.javascript import process_js_environment
from license_grep.licenses import UnknownLicense, license_name_map
from license_grep.output import (
    OutputOptions,
    write_grouped_markdown,
    write_json,
    write_license_table,
)
from license_grep.input.python import process_python_environment


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--js", dest="javascript_roots", action="append", default=[])
    ap.add_argument("--py", dest="python_roots", action="append", default=[])
    ap.add_argument("--dart", dest="dart_roots", action="append", default=[])
    ap.add_argument("--write-json", required=False, type=argparse.FileType("w"))
    ap.add_argument("--write-table", required=False, type=argparse.FileType("w"))
    ap.add_argument(
        "--write-grouped-markdown", required=False, type=argparse.FileType("w")
    )
    ap.add_argument("--strip-versions", default=False, action="store_true")
    ap.add_argument("--dump-unknown-licenses", default=False, action="store_true")
    ap.add_argument(
        "--bsd", default="BSD-3-Clause", help="Map 'BSD' to this BSD license variant"
    )
    ap.add_argument("--dart-pub-cache", required=False, help="path to dart .pub-cache")
    args = ap.parse_args()

    license_name_map.setdefault("BSD", args.bsd)
    license_name_map["BSD License"] = args.bsd

    package_infos = []

    for js_root in args.javascript_roots:
        package_infos.extend(process_js_environment(js_root))

    for py_root in args.python_roots:
        package_infos.extend(process_python_environment(py_root))

    for dart_root in args.dart_roots:
        package_infos.extend(
            process_dart_environment(dart_root, pub_cache=args.dart_pub_cache)
        )

    print(f"{len(package_infos):d} packages found.", file=sys.stderr)
    n_unknown = 0
    n_unlicensed = 0
    for pkg_info in package_infos:
        if not pkg_info.licenses:
            n_unlicensed += 1
            print(f"No licenses found for {pkg_info.spec}")
        else:
            for lic in pkg_info.licenses:
                if isinstance(lic, UnknownLicense):
                    n_unknown += 1
                    if args.dump_unknown_licenses:
                        print(f"Unknown license for {pkg_info.spec}: <{lic}>")
    if n_unknown:
        print(f"{n_unknown} unknown licenses.", file=sys.stderr)
    if n_unlicensed:
        print(
            f"{n_unlicensed} packages for which no license was found.", file=sys.stderr
        )

    if args.write_json:
        oo = OutputOptions(strip_versions=args.strip_versions, fp=args.write_json)
        write_json(package_infos, oo)
        print(f"JSON written to {args.write_json.name}", file=sys.stderr)

    if args.write_table:
        oo = OutputOptions(strip_versions=args.strip_versions, fp=args.write_table)
        write_license_table(package_infos, oo)
        print(f"Markdown table written to {args.write_table.name}", file=sys.stderr)

    if args.write_grouped_markdown:
        oo = OutputOptions(
            strip_versions=args.strip_versions, fp=args.write_grouped_markdown
        )
        write_grouped_markdown(package_infos, oo)
        print(
            f"Markdown written to {args.write_grouped_markdown.name}", file=sys.stderr
        )
