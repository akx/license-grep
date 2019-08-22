import os
import sys
from typing import Iterable

from license_grep.deduction import deduce_license_from_dir
from license_grep.input.cache_dir_utils import get_cache_map
from license_grep.models import PackageInfo

try:
    import toml
except ImportError as ie:
    toml = ie


def process_rust_package(package_dir):
    cargo_toml_path = os.path.join(package_dir, "Cargo.toml")
    with open(cargo_toml_path) as fp:
        cargo_toml_content = toml.load(fp)
    toml_package_info = cargo_toml_content["package"]
    toml_license = toml_package_info.get("license")
    pkg_info = PackageInfo(
        name=toml_package_info["name"],
        version=toml_package_info["version"],
        type="Rust",
        location=cargo_toml_path,
        context=None,
        raw_licenses=(toml_license.split("/") if toml_license else []),
    )

    if not pkg_info.raw_licenses:
        deduced_license = deduce_license_from_dir(package_dir)
        if deduced_license:
            pkg_info.raw_licenses = [deduced_license]
    return pkg_info


def process_rust_environment(root_directory, cargo_home=None) -> Iterable[PackageInfo]:
    if not cargo_home:
        cargo_home = os.path.expanduser(os.environ.get("CARGO_HOME", "~/.cargo"))

    cargo_lock_path = os.path.join(root_directory, "Cargo.lock")
    if not os.path.isfile(cargo_lock_path):
        raise RuntimeError(f"Not found: {cargo_lock_path}")
    if isinstance(toml, Exception):
        raise RuntimeError(
            f"TOML library (toml) not installed, unable to process Rust"
        ) from toml

    with open(cargo_lock_path) as fp:
        cargo_lock_content = toml.load(fp)

    cache_map = get_cache_map(os.path.join(cargo_home, "registry", "src"))

    for pkg_dict in cargo_lock_content.get("package", []):
        name = pkg_dict["name"]
        version = pkg_dict["version"]
        cache_key = (name, version)
        package_dir = cache_map.get(cache_key)
        if not package_dir:
            print(
                f"Rust package {name}@{version} not found in cargo cache",
                file=sys.stderr,
            )
        else:
            rup = process_rust_package(package_dir)
            rup.context = root_directory
            yield rup
