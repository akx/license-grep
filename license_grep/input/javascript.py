import json
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from typing import Iterable, Optional

from license_grep.deduction import deduce_license_from_dir
from license_grep.models import PackageInfo
from license_grep.utils import is_excluded_dir


def find_js_manifests(base_path):
    for path, dirs, files in os.walk(base_path):
        dirs[:] = [dir for dir in dirs if not is_excluded_dir(dir)]
        for filename in files:
            if filename == "package.json":
                path = os.path.join(path, filename)
                if "/test/" not in path:
                    yield path


def process_js_manifest(package_json_path, allow_parent=True) -> Optional[PackageInfo]:
    package_json_dir = os.path.dirname(package_json_path)
    with open(package_json_path) as fp:
        data = json.load(fp)
    name = data.get("name")
    version = data.get("version")
    if not name or data.get("private"):
        return None

    raw_licenses = data.get("licenses", [])
    if raw_licenses:
        raw_licenses = [l["type"] for l in raw_licenses]
    else:
        package_json_license = data.get("license")
        if package_json_license:
            if isinstance(package_json_license, dict):
                package_json_license = package_json_license["type"]
            raw_licenses = [package_json_license]

    pkg_info = PackageInfo(
        name=name,
        version=version,
        type="JavaScript",
        location=package_json_path,
        context=None,
        raw_licenses=raw_licenses,
    )

    if not raw_licenses:
        deduced_license = deduce_license_from_dir(package_json_dir)
        if deduced_license:
            pkg_info.raw_licenses = [deduced_license]
        else:
            if allow_parent:
                parent_node_manifest = os.path.join(
                    package_json_dir, "..", "package.json"
                )
                if os.path.isfile(parent_node_manifest):
                    parent_pkg_info = process_js_manifest(
                        parent_node_manifest, allow_parent=False
                    )
                    if parent_pkg_info:
                        print(
                            f"{package_json_path}: using parent {parent_node_manifest} licenses for license",
                            file=sys.stderr,
                        )
                        pkg_info.raw_licenses = parent_pkg_info.raw_licenses

    if not pkg_info.raw_licenses:
        print(f"No license: {package_json_path}", file=sys.stderr)

    if not version:
        print(f"No version: {package_json_path}", file=sys.stderr)

    return pkg_info


def process_js_environment(directory) -> Iterable[PackageInfo]:
    manifests = find_js_manifests(directory)
    with ThreadPool() as pool:
        for package_info in pool.imap_unordered(process_js_manifest, manifests):
            if package_info:
                package_info.context = directory
                yield package_info
