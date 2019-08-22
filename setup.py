import ast
import os
import re
import setuptools

with open(
    os.path.join(os.path.dirname(__file__), "license_grep", "__init__.py")
) as infp:
    version = ast.literal_eval(
        re.search("__version__ = (.+?)$", infp.read(), re.M).group(1)
    )

dev_dependencies = ["flake8", "isort", "pydocstyle", "pytest-cov"]

if __name__ == "__main__":
    setuptools.setup(
        name="license-grep",
        version=version,
        license="MIT",
        install_requires=[],
        tests_require=dev_dependencies,
        extras_require={"dev": dev_dependencies},
        packages=setuptools.find_packages(".", include=("license_grep*",)),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
