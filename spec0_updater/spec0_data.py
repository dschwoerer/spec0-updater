# from https://scientific-python.org/specs/spec-0000/

import requests
import collections
from datetime import datetime, timedelta

import pandas as pd
from packaging.version import Version


py_releases = {
    "3.8": "Oct 14, 2019",
    "3.9": "Oct 5, 2020",
    "3.10": "Oct 4, 2021",
    "3.11": "Oct 24, 2022",
    "3.12": "Oct 2, 2023",
    "3.13": "Oct 7, 2024",
}
core_packages = [
    # Path(x).stem for x in glob("../core-projects/*.md") if "_index" not in x
    "numpy",
    "scipy",
    "matplotlib",
    "pandas",
    "scikit-image",
    "networkx",
    "scikit-learn",
    "xarray",
    "ipython",
    "zarr",
]
plus36 = timedelta(days=int(365 * 3))
plus24 = timedelta(days=int(365 * 2))

# Release data

# put cutoff 3 quarters ago – we do not use "just" -9 month,
# to avoid the content of the quarter to change depending on when we generate this
# file during the current quarter.

current_date = pd.Timestamp.now()
current_quarter_start = pd.Timestamp(
    current_date.year, (current_date.quarter - 1) * 3 + 1, 1
)
cutoff = current_quarter_start - pd.DateOffset(months=9)


def get_release_dates(package, support_time=plus24):
    releases = {}

    print(f"Querying pypi.org for {package} versions...", end="", flush=True)
    response = requests.get(
        f"https://pypi.org/simple/{package}",
        headers={"Accept": "application/vnd.pypi.simple.v1+json"},
    ).json()
    print("OK")

    file_date = collections.defaultdict(list)
    for f in response["files"]:
        ver = f["filename"].split("-")[1]
        try:
            version = Version(ver)
        except:
            continue

        if version.is_prerelease or version.micro != 0:
            continue

        release_date = None
        for format in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                release_date = datetime.strptime(f["upload-time"], format)
            except:
                pass

        if not release_date:
            continue

        file_date[version].append(release_date)

    release_date = {v: min(file_date[v]) for v in file_date}

    for ver, release_date in sorted(release_date.items()):
        drop_date = release_date + support_time
        if drop_date >= cutoff:
            releases[ver] = {
                "release_date": release_date,
                "drop_date": drop_date,
            }

    return releases


package_releases = {
    "python": {
        version: {
            "release_date": datetime.strptime(release_date, "%b %d, %Y"),
            "drop_date": datetime.strptime(release_date, "%b %d, %Y") + plus36,
        }
        for version, release_date in py_releases.items()
    }
}

package_releases |= {package: get_release_dates(package) for package in core_packages}

# filter all items whose drop_date are in the past
package_releases = {
    package: {
        version: dates
        for version, dates in releases.items()
        if dates["drop_date"] > current_date
    }
    for package, releases in package_releases.items()
}

# print(package_releases)

pkg_vers_min = {pkg: sorted(vers)[0] for pkg, vers in package_releases.items()}

print(pkg_vers_min)
