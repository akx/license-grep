import pkg_resources

from license_grep.deduction import convert_nonstandard_license_name


def unique_in_order(iter):
    seen = set()
    for obj in iter:
        if obj not in seen:
            seen.add(obj)
            yield obj


def process_dist(dist):
    license = None
    metadata = None
    if dist.has_metadata("PKG-INFO"):
        metadata = dist.get_metadata("PKG-INFO")
    if dist.has_metadata("METADATA"):
        metadata = dist.get_metadata("METADATA")
    if metadata:
        licenses = list(
            unique_in_order(
                convert_nonstandard_license_name(name)
                for name in find_licenses(metadata)
            )
        )
        license = '/'.join(licenses)
    return {
        "%s@%s"
        % (dist.project_name, dist.version): {
            "via": "python",
            "version": dist.version,
            "license": license or None,
        }
    }


def find_licenses(metadata):
    for line in metadata.splitlines():
        if line.startswith("License:"):
            license = line.split(None, 1)[-1]
            if license and "unknown" not in license.lower():
                yield license.split(" :: ")[-1]
        if line.startswith("Classifier:"):
            classifier = line.split(" ", 1)[-1]
            if classifier.startswith("License"):
                yield classifier.split(" :: ")[-1]


def process_python_environment(data):
    for dist in pkg_resources.working_set:
        data.update(process_dist(dist))
