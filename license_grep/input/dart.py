import os
import sys
from typing import Iterable

from license_grep.deduction import deduce_license_from_dir
from license_grep.input.cache_dir_utils import get_cache_map
from license_grep.models import PackageInfo

try:
    import yaml
except ImportError as ie:
    yaml = ie


def process_dart_package(package_dir):
    pubspec_yaml_path = os.path.join(package_dir, "pubspec.yaml")
    with open(pubspec_yaml_path) as fp:
        pubspec_yaml_content = yaml.safe_load(fp)
    yaml_license = pubspec_yaml_content.get("license")
    pkg_info = PackageInfo(
        name=pubspec_yaml_content["name"],
        version=pubspec_yaml_content["version"],
        type="Dart",
        location=pubspec_yaml_path,
        context=None,
        raw_licenses=([yaml_license] if yaml_license else []),
    )

    if not pkg_info.raw_licenses:
        deduced_license = deduce_license_from_dir(package_dir)
        if deduced_license:
            pkg_info.raw_licenses = [deduced_license]
    return pkg_info


def process_dart_environment(root_directory, pub_cache) -> Iterable[PackageInfo]:
    pubspec_lock_path = os.path.join(root_directory, "pubspec.lock")
    if not os.path.isfile(pubspec_lock_path):
        raise RuntimeError(f"Not found: {pubspec_lock_path}")
    if isinstance(yaml, Exception):
        raise RuntimeError(
            f"YAML library (PyYAML) not installed, unable to process Dart"
        ) from yaml
    if not (pub_cache and os.path.isdir(pub_cache)):
        raise RuntimeError(
            "pub_cache not set or does not exist, unable to process Dart"
        )

    with open(pubspec_lock_path) as fp:
        pubspec_lock_content = yaml.safe_load(fp)

    package_ids = [
        (name, info["version"])
        for (name, info) in pubspec_lock_content["packages"].items()
    ]
    cache_map = get_cache_map(pub_cache)
    for package_id in package_ids:
        if package_id in cache_map:
            darp = process_dart_package(cache_map[package_id])
            darp.context = root_directory
            yield darp
        else:
            print(f"Dart package {package_id} not found in pub cache", file=sys.stderr)
