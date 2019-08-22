import io
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import List

from license_grep.models import PackageInfo


@dataclass
class OutputOptions:
    fp: io.TextIOBase
    strip_versions: bool


def write_license_table(package_infos: List[PackageInfo], oo: OutputOptions):
    oo.fp.write("""| type | name | license |\n| ---- | ---- | ------- |\n""")
    for pkgi in sorted(package_infos, key=lambda pkgi: pkgi.full_spec):
        name = pkgi.name if oo.strip_versions else pkgi.spec
        oo.fp.write(f"| {pkgi.type} | {name} | {pkgi.licenses_string} |\n")


def write_json(package_infos: List[PackageInfo], oo: OutputOptions):
    json.dump(
        {pkg_info.full_spec: pkg_info.as_json_dict() for pkg_info in package_infos},
        fp=oo.fp,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def write_grouped_markdown(package_infos: List[PackageInfo], oo: OutputOptions):
    packages_by_license = defaultdict(dict)
    for pkgi in package_infos:
        package_key = (pkgi.type, pkgi.name) if oo.strip_versions else pkgi.full_spec
        packages_by_license[pkgi.licenses_string][package_key] = pkgi
    for license, pgki_map in sorted(packages_by_license.items(), key=str):
        for _key, pkgi in sorted(pgki_map.items()):
            name = pkgi.name if oo.strip_versions else pkgi.spec
            print(f"* {license}: {name} ({pkgi.type})", file=oo.fp)
