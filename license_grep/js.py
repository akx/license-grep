import json
import os
import subprocess
import sys

from license_grep.utils import is_excluded_dir


def find_js_manifests(base_path):
    for path, dirs, files in os.walk(base_path):
        dirs[:] = [dir for dir in dirs if not is_excluded_dir(dir)]
        for filename in files:
            if filename in ("package.json", "bower.json"):
                yield os.path.join(path, filename)


def process_js_manifest(node_manifest):
    dirname = os.path.realpath(os.path.dirname(node_manifest))
    bin_path = os.path.realpath(os.path.join(os.getcwd(), 'node_modules', '.bin'))

    if node_manifest.endswith("package.json"):
        cmd = f"{bin_path}/license-checker --json"
        via = "npm"
    else:
        raise NotImplementedError("Not implemented")

    json_data, _ = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, cwd=dirname
    ).communicate()

    data = json.loads(json_data.decode("UTF-8"))
    for item in list(data.values()):
        item["via"] = via
    return data


def process_js_environment(data):
    for manifest in find_js_manifests("."):
        print("Processing: %s" % manifest, file=sys.stderr)
        data.update(process_js_manifest(manifest))
