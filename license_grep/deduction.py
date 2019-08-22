import os
import sys


def deduce_license_from_text(text):
    text = (
        text.replace("\n\n", "*PARA*")
        .replace("\n", " ")
        .replace("*PARA*", "\n\n")
        .replace("'", '"')
    )
    if "The MIT License" in text:
        return "MIT"
    if "Licensed under the MIT license." in text:
        return "MIT"
    if "License\n\nMIT" in text:
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
    return None


def deduce_license_from_dir(directory):
    for filename in os.listdir(directory):
        lower_name = filename.lower()
        filename = os.path.join(directory, filename)
        if (
            lower_name.startswith("license")
            or lower_name.startswith("readme")
            or lower_name.startswith("copying")
        ):
            with open(filename, "r") as license_fp:
                license = deduce_license_from_text(license_fp.read())
                if license:
                    print(
                        f"Used file {filename} to find license {license} for {directory}",
                        file=sys.stderr,
                    )
                    return license
