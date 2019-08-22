import json
from collections import defaultdict


def write_license_table(data, fp):
    for package, info in sorted(data.items()):
        licenses = info.get("license") or info.get("licenses")
        if isinstance(licenses, list):
            licenses = ", ".join(sorted(licenses))
        fp.write("| %s | %s | %s |\n" % (info["via"], package, licenses))


def write_json(data, fp):
    json.dump(data, fp, sort_keys=True)


def write_grouped_markdown(data, fp):
    packages_by_license = defaultdict(list)
    for package in data.values():
        packages_by_license[package['license']].append(package)
    for license, packages in sorted(packages_by_license.items(), key=str):
        # packages_by_via = defaultdict(list)
        # for package in packages:
        #     packages_by_via[package['via']].append(package)
        print(f'# {license}\n', file=fp)
        for package in packages:
            print(f'* {package["spec"]} ({package["via"]})', file=fp)
        print(file=fp)
