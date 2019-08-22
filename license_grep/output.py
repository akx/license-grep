import json


def write_license_table(data, fp):
    for package, info in sorted(data.items()):
        licenses = info.get("license") or info.get("licenses")
        if isinstance(licenses, list):
            licenses = ", ".join(sorted(licenses))
        fp.write("| %s | %s | %s |\n" % (info["via"], package, licenses))


def write_json(data, fp):
    json.dump(data, fp, sort_keys=True)
