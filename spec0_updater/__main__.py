import tomlkit
from tomlkit import parse, dumps
import sys

if 1:
    import spec0_data

    pkgs = spec0_data.pkg_vers_min
else:
    from packaging.version import Version

    pkgs = {
        "python": "3.11",
        "numpy": Version("1.26.0"),
        "scipy": Version("1.12.0"),
        "matplotlib": Version("3.8.0"),
        "pandas": Version("2.1.0"),
        "scikit-image": Version("0.22.0"),
        "networkx": Version("3.2"),
        "scikit-learn": Version("1.3.0"),
        "xarray": Version("2023.7.0"),
        "ipython": Version("8.15.0"),
        "zarr": Version("2.16.0"),
    }


def update(toml):
    for i, pv in enumerate(toml):
        try:
            pkg, ver = [x.strip() for x in pv.split(">=")]
            if pkg in pkgs and ver != f"{pkgs[pkg]}":
                print(f"Update {pkg} from {ver} to {pkgs[pkg]}")
                toml[i] = f"{pkg} >= {pkgs[pkg]}"
        except:
            for p in pkgs:
                if p in pv:
                    print(
                        f"Failed to parse `{pv}` but might match {p} - update to {pkgs[p]}"
                    )


def updateall(toml, func):
    for k in toml:
        if isinstance(toml[k], dict):
            updateall(toml[k], func)
        else:
            if k in ("requires", "dependencies"):
                func(toml[k])
            elif k == "requires-python":
                toml[k] = f">= {pkgs['python']}"
            elif k == "optional-dependencies":
                for d in toml[k].values():
                    func(d)


def runit(fn):
    with open(fn) as f:
        toml = parse(f.read())

    updateall(toml, update)

    with open(fn, "w") as f:
        f.write(dumps(toml))


dirs = sys.argv[1:] or ["."]

for d in dirs:
    runit(f"{d}/pyproject.toml")
