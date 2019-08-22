from typing import Iterable

import pkg_resources

from license_grep.models import PackageInfo

PYTHON_LICENSE_BLACKLIST = {"OSI Approved", "License:"}


def process_dist(dist: pkg_resources.Distribution):
    licenses = None
    metadata = None
    location = None
    for metadata_filename in ("METADATA", "PKG-INFO"):
        if dist.has_metadata(metadata_filename):
            metadata = dist.get_metadata(metadata_filename)
            location = dist._get_metadata_path_for_display(metadata_filename)
    if metadata:
        licenses = list(
            license
            for license in find_licenses(metadata)
            if license not in PYTHON_LICENSE_BLACKLIST
        )
    return PackageInfo(
        name=dist.project_name,
        version=dist.version,
        raw_licenses=licenses,
        location=(location or dist.location),
        type="Python",
        context=None,
    )


def find_licenses(metadata):
    for line in metadata.splitlines():
        if line.startswith("License:"):
            license = line.split(None, 1)[-1]
            if license and "unknown" not in license.lower():
                yield license.split(" :: ")[-1]
        if line.startswith("Classifier:"):
            classifier = line.split(" ", 1)[-1]
            if classifier.startswith("License"):
                yield classifier.split(" :: ")[-1]


def process_python_environment(root_directory) -> Iterable[PackageInfo]:
    env = pkg_resources.Environment(search_path=[root_directory])
    for name in env:
        for dist in env[name]:
            pkginfo = process_dist(dist)
            if pkginfo:
                pkginfo.context = root_directory
                yield pkginfo
