import pkg_resources


def process_dist(dist):
    license = None
    metadata = None
    if dist.has_metadata('PKG-INFO'):
        metadata = dist.get_metadata('PKG-INFO')
    if dist.has_metadata('METADATA'):
        metadata = dist.get_metadata('METADATA')
    if metadata:
        license = find_license(metadata)
    return {
        "%s@%s"
        % (dist.project_name, dist.version): {
            "via": "python",
            "version": dist.version,
            "license": license or "<no license found>",
        }
    }


def find_license(metadata):
    for line in metadata.splitlines():
        if line.startswith("License:"):
            license = line.split(None, 1)[-1]
            if license and "unknown" not in license.lower():
                return license
        if line.startswith("Classifier:"):
            classifier = line.split(" ", 1)[-1]
            if classifier.startswith("License"):
                return classifier.split(" :: ")[-1]


def process_python_environment(data):
    for dist in pkg_resources.working_set:
        data.update(process_dist(dist))
