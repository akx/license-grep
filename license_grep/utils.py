from fnmatch import fnmatch

EXCLUDE_PATTERNS = [
    ".git",
    "__pycache__",
    "contrib",
    "docs",
    "LC_MESSAGES",
    "tests*",
    "var",
    "venv*",
]


def is_excluded_dir(dir):
    return any(fnmatch(dir, pat) for pat in EXCLUDE_PATTERNS)


def strip_versions(data):
    out_data = {}
    for key, value in sorted(list(data.items()), reverse=True):
        key = key.split("@")[0]
        out_data[key] = value
    return out_data
