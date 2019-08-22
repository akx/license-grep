from fnmatch import fnmatch

EXCLUDE_PATTERNS = [".git", "__pycache__", "LC_MESSAGES"]


def is_excluded_dir(dir):
    return any(fnmatch(dir, pat) for pat in EXCLUDE_PATTERNS)


def unique_in_order(lst):
    seen = set()
    for obj in lst:
        if obj not in seen:
            seen.add(obj)
            yield obj
