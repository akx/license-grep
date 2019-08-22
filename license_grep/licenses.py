import json
import os
import re
from typing import Iterable, Optional, Tuple, Union

with open(os.path.join(os.path.dirname(__file__), "licenses.json")) as fp:
    spdx_licenses = json.load(fp)["licenses"]

spdx_name_to_id = {l["name"].lower(): l["licenseId"] for l in spdx_licenses}
spdx_ids = {l["licenseId"] for l in spdx_licenses}

license_name_map = {
    "2-Clause BSD": "BSD-2-Clause",
    "3-Clause BSD License": "BSD-3-Clause",
    "AFLv2.1": "AFL-2.1",
    "Apache 2.0": "Apache-2.0",
    "Apache License, Version 2.0": "Apache-2.0",
    "Apache Software License 2.0": "Apache-2.0",
    "Apache Software License": "Apache-2.0",  # TODO: is this mapping correct?
    "Apache": "Apache-2.0",  # TODO: is this mapping correct?
    "Apache-2": "Apache-2.0",
    "ASL 2": "Apache-2.0",
    "BSD 3-Clause License": "BSD-3-Clause",
    "BSD License": "BSD",  # Replaced during initialization
    "GPLv2+": "GPL-2.0+",
    "GPLv3+": "GPL-3.0+",
    "LGPLv2+": "LGPL-2.0+",
    "LGPLv3+": "LGPL-3.0+",
    "MIT License": "MIT",
    "MIT no attribution": "MIT-0",
    "MIT/X11": "MIT",
    "Modified BSD License": "BSD-3-Clause",
    "Mozilla Public License 1.1 (MPL 1.1)": "MPL-1.1",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "new BSD License": "BSD-3-Clause",
    "PSF": "Python-2.0",
    "PSFL": "Python-2.0",
    "Python Software Foundation License": "Python-2.0",
    "Python Software Foundation": "Python-2.0",
    "Zope Public License": "ZPL-2.1",
    "ZPL 2.1": "ZPL-2.1",
    "ZPL": "ZPL-2.1",
}

license_endswith_map = {
    "(GPLv2+)": "GPL-2.0+",
    "(GPLv3+)": "GPL-3.0+",
    "(LGPLv2+)": "LGPL-2.0+",
    "(LGPLv3+)": "LGPL-3.0+",
    "(LGPL)": "LGPL",
    "(HPND)": "HPND",
}


class UnknownLicense(str):
    def __repr__(self):
        return f"UnknownLicense({str.__repr__(self)})"


def canonicalize_license(name) -> Optional[str]:
    if name in spdx_ids:
        return name
    if name.lower() in spdx_name_to_id:
        return spdx_name_to_id[name.lower()]
    if name in license_name_map:
        return license_name_map[name]
    for endswith, result in license_endswith_map.items():
        if name.endswith(endswith):
            return result


def _canonicalize_licenses(raw_licenses) -> Iterable[Tuple[str, Union[str, None]]]:
    for atom in raw_licenses or []:
        if not atom:
            yield (atom, None)
            continue

        atom = atom.replace("Apache License, Version 2.0", "Apache-2.0")

        canonicalized_atom = canonicalize_license(atom)

        if canonicalized_atom:
            yield (atom, canonicalized_atom)
            continue

        if ", " in atom and ", Version" not in atom:
            for bit in atom.split(", "):
                yield (atom, canonicalize_license(bit))
            continue

        if " or " in atom and "or later" not in atom:
            for bit in atom.split(" or "):
                yield (atom, canonicalize_license(bit))
            continue

        if atom.startswith("(") or " OR " in atom or " AND " in atom:
            # TODO: considering AND/OR the same is maybe a little iffy
            for bit in re.split("(?: AND | OR )", atom.strip("()")):
                yield (atom, canonicalize_license(bit))
            continue

        yield (atom, canonicalized_atom)


def canonicalize_licenses(
    raw_licenses
) -> Iterable[Tuple[str, Union[str, UnknownLicense, None]]]:
    for atom, canonicalized_atom in _canonicalize_licenses(raw_licenses):
        if not canonicalized_atom:
            canonicalized_atom = UnknownLicense(atom)
        if canonicalized_atom and canonicalized_atom not in spdx_ids:
            canonicalized_atom = UnknownLicense(canonicalized_atom)
        yield (atom, canonicalized_atom)
