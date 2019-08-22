# -*- coding: utf-8 -*-

import sys

from fnmatch import fnmatch
from pip import get_installed_distributions
import argparse
import json
import os
import subprocess


EXCLUDE_PATTERNS = [
    'contrib',
    'docs',
    'tests*',
    'node_modules',
    'bower_components',
    'var',
    '__pycache__',
    'LC_MESSAGES',
    'venv*',
]


def is_excluded_dir(dir):
    return any(fnmatch(dir, pat) for pat in EXCLUDE_PATTERNS)


def process_dist(dist):
    license = None
    metadata = None
    if dist.has_metadata('PKG-INFO'):
        metadata = dist.get_metadata('PKG-INFO')
    if dist.has_metadata('METADATA'):
        metadata = dist.get_metadata('METADATA')
    if metadata:
        license = find_license(metadata)
    return {
        "%s@%s"
        % (dist.project_name, dist.version): {
            "via": "python",
            "version": dist.version,
            "license": license or "<no license found>",
        }
    }


def find_license(metadata):
    for line in metadata.splitlines():
        if line.startswith("License:"):
            license = line.split(None, 1)[-1]
            if license and "unknown" not in license.lower():
                return license
        if line.startswith("Classifier:"):
            classifier = line.split(" ", 1)[-1]
            if classifier.startswith("License"):
                return classifier.split(" :: ")[-1]


def find_node_manifests(base_path):
    for path, dirs, files in os.walk(base_path):
        dirs[:] = [dir for dir in dirs if not is_excluded_dir(dir)]
        for filename in files:
            if filename in ("package.json", "bower.json"):
                yield os.path.join(path, filename)


def process_node_manifest(node_manifest):
    dirname = os.path.realpath(os.path.dirname(node_manifest))

    if node_manifest.endswith("package.json"):
        cmd = "license-checker -e json"
        via = "npm"
    elif node_manifest.endswith("bower.json"):
        cmd = "bower-license -e json"
        via = "bower"
    else:
        raise NotImplementedError("Not implemented")

    json_data, _ = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, cwd=dirname
    ).communicate()

    data = json.loads(json_data.decode("UTF-8"))
    for item in list(data.values()):
        item["via"] = via
    return data


def read_data_from_env():
    data = {}
    for manifest in find_node_manifests("."):
        print("Processing: %s" % manifest, file=sys.stderr)
        data.update(process_node_manifest(manifest))

    print("Processing Python environment")
    for dist in get_installed_distributions(local_only=True):
        data.update(process_dist(dist))
    return data


def write_license_table(data, fp):
    for package, info in sorted(data.items()):
        licenses = info.get("license") or info.get("licenses")
        if isinstance(licenses, list):
            licenses = ", ".join(sorted(licenses))
        fp.write("| %s | %s | %s |\n" % (info["via"], package, licenses))


def strip_versions(data):
    out_data = {}
    for key, value in sorted(list(data.items()), reverse=True):
        key = key.split("@")[0]
        out_data[key] = value
    return out_data


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
        json.dump(data, args.write_json, sort_keys=True)
        print("JSON written to %s" % args.write_json.name)

    if args.write_table:
        write_license_table(data, fp=args.write_table)
        print("Markdown table written to %s" % args.write_table.name)


if __name__ == "__main__":
    main()
