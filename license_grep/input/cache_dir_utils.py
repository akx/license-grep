import os
import re
from functools import lru_cache


@lru_cache()
def get_cache_map(cache_dir, pattern="^(.+)-(\d+.*)$"):
    cache_map = {}
    for path, dirs, files in os.walk(cache_dir):
        for dir in dirs:
            m = re.match(pattern, dir)
            if m:
                cache_map[m.groups()] = os.path.join(path, dir)
    return cache_map
