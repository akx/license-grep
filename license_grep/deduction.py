import os
import re


def deduce_license_from_text(text):
    text = (
        text.replace("\n\n", "*PARA*")
        .replace("\n", " ")
        .replace("*PARA*", "\n\n")
        .replace("'", '"')
    )
    if "The MIT License" in text:
        return "MIT"
    if all(
        [
            "Permission is hereby granted, free of charge, to any person obtaining a copy"
            in text,
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
            in text,
        ]
    ):
        return "MIT"
    if (
        "Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:"
        in text
    ):
        return "BSD"
    if "License\n\nMIT" in text:
        return "MIT"

    print(text)
    raise NotImplementedError("...")


def deduce_license_from_dir(directory):
    # mit_license_file = os.path.join(directory, 'LICENSE-MIT')
    # if os.path.isfile(mit_license_file):
    #     return 'MIT'
    #
    license_containing_files = [
        os.path.join(directory, "LICENSE"),
        os.path.join(directory, "LICENSE-MIT"),
        os.path.join(directory, "README.md"),
    ]
    for file in license_containing_files:
        if os.path.isfile(file):
            with open(file, "r") as license_fp:
                license = deduce_license_from_text(license_fp.read())
                if license:
                    return license


nonstandard_license_name_map = {
    'Python Software Foundation': 'PSFL',
    'Apache Software License': 'Apache',
    'MIT License': 'MIT',
}

nonstandard_license_substring_map = [
    ('(GPL)', 'GPL'),
    ('Mozilla Public License 2.0', 'MPL-2.0'),
    ('LGPLv3+', 'LGPLv3+'),
    ('LGPLv2+', 'LGPLv2+'),
    ('GPLv2+', 'GPLv2+'),
    ('(LGPL)', 'LGPL'),
]


def convert_nonstandard_license_name(license):
    if not license:
        return 'Unknown'
    if license in nonstandard_license_name_map:
        return nonstandard_license_name_map[license]
    for needle, result in nonstandard_license_substring_map:
        if needle in license:
            return result
    license_l = license.lower()
    if license_l in ('apache 2.0', 'apache license 2.0', 'apache license, version 2.0'):
        return 'Apache-2.0'
    return re.sub(' License$', '', license)
