import json
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

from license_grep.deduction import deduce_license_from_dir
from license_grep.utils import is_excluded_dir


def find_js_manifests(base_path):
    for path, dirs, files in os.walk(base_path):
        dirs[:] = [dir for dir in dirs if not is_excluded_dir(dir)]
        for filename in files:
            if filename == "package.json":
                path = os.path.join(path, filename)
                if "/test/" not in path:
                    yield path


def process_js_manifest(package_json_path, spec_override=None, allow_parent=True):
    package_json_dir = os.path.dirname(package_json_path)
    with open(package_json_path) as fp:
        data = json.load(fp)
    name = data.get("name")
    version = data.get("version")
    if not name or data.get("private"):
        return None

    spec = f"{name}@{(version or '?')}"

    licenses = data.get("licenses", [])
    if licenses:
        licenses = [l["type"] for l in licenses]
        license = "(%s)" % " OR ".join(licenses) if len(licenses) > 1 else licenses[0]
    else:
        license = data.get("license")

    if not license:
        license = deduce_license_from_dir(package_json_dir)
        if not license:
            if allow_parent:
                parent_node_manifest = os.path.join(
                    package_json_dir, "..", "package.json"
                )
                if os.path.isfile(parent_node_manifest):
                    manifest = process_js_manifest(
                        parent_node_manifest, spec_override=spec, allow_parent=False
                    )
                    if manifest:
                        print(
                            f"{package_json_path}: using parent {parent_node_manifest} for license",
                            file=sys.stderr,
                        )
                        return manifest
            print(f"No license: {package_json_path}", file=sys.stderr)
            return None
    if not version:
        print(f"No version: {package_json_path}", file=sys.stderr)

    return {(spec_override or spec): {"via": "js", "license": license}}


def process_js_environment(data, directory):
    manifests = find_js_manifests(directory)
    with ThreadPool() as pool:
        for manifest in pool.imap_unordered(process_js_manifest, manifests):
            if manifest:
                data.update(manifest)
