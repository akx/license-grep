from dataclasses import asdict, dataclass
from typing import List, Optional

from license_grep.licenses import UnknownLicense, canonicalize_licenses
from license_grep.utils import unique_in_order


@dataclass
class PackageInfo:
    name: str
    version: str
    type: str
    raw_licenses: Optional[List[str]]
    location: str
    context: Optional[str]

    @property
    def licenses(self):
        for license, canonicalized_license in canonicalize_licenses(self.raw_licenses):
            yield canonicalized_license

    @property
    def licenses_string(self):
        return ", ".join(
            unique_in_order(str(license or "<UNKNOWN>") for license in self.licenses)
        )

    @property
    def spec(self):
        return f"{self.name}@{self.version}"

    @property
    def full_spec(self):
        return f"{self.type}:{self.name}@{self.version}"

    def as_json_dict(self):
        return {
            **asdict(self),
            "licenses": list(
                unique_in_order(
                    f"?{l}" if isinstance(l, UnknownLicense) else l
                    for l in self.licenses
                )
            ),
            "spec": self.spec,
        }
