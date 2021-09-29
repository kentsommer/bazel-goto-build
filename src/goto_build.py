#!/usr/bin/python3

from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.request, urllib.parse, urllib.error

HOME = Path.home()
# Paths.
LOOKUP_DATA_DIR = HOME / ".goto_build"
LOOKUP_DATA_PATH = LOOKUP_DATA_DIR / "build_lookup.json"
CUSTOM_BUILDOZER_PATH = LOOKUP_DATA_DIR / "buildozer"
# Buildozer details.
CUSTOM_BUILDOZER_URL = "https://github.com/kentsommer/buildtools/releases/download/4.2.0-1/buildozer"
CUSTOM_BUILDOZER_SHA = "9a9193b77f51dcff416cdc5039a7a78e7b7ace7b019c1c952ab8028e6ee3303f"


def sha256sum(path):
    """Calculates sha256sum of the file at the given path."""
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path, mode="rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def make_executable(path):
    """Makes the file at the given path executable."""
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def fetch_buildozer():
    """Download custom buildozer."""
    # Prepare our directory if it doesn't exist.
    os.makedirs(LOOKUP_DATA_DIR, exist_ok=True)
    # Download buildozer binary.
    buildozer_binary = urllib.request.urlopen(CUSTOM_BUILDOZER_URL).read()
    with open(CUSTOM_BUILDOZER_PATH, mode="wb") as fp:
        fp.write(buildozer_binary)
    make_executable(CUSTOM_BUILDOZER_PATH)


def maybe_fetch_buildozer():
    """Download custom buildozer if not downloaded already."""
    if os.path.isfile(CUSTOM_BUILDOZER_PATH):
        if sha256sum(CUSTOM_BUILDOZER_PATH) != CUSTOM_BUILDOZER_SHA:
            fetch_buildozer()
    else:
        fetch_buildozer()


def build_lookup_data():
    """Build map from file path to corresponding BUILD file and target."""
    lookup_data = subprocess.check_output(
        [
            CUSTOM_BUILDOZER_PATH,
            "print startline path srcs hdrs",
            "//...:*",
        ],
        stderr=subprocess.DEVNULL,
    ).decode("utf-8")
    pattern = re.compile(
        r"^(\d*) (\/.*?BUILD).*?(?:\[(.*?)\]|glob\((.*?)\)|(\(missing\))).*?(?:\[(.*?)\]|glob\((.*?)\)|(\(missing\)))",
        re.DOTALL + re.MULTILINE,
    )
    matches = pattern.findall(lookup_data)
    result = {}
    for match in matches:
        line = match[0]
        BUILD = match[1]
        prefix = BUILD.split("BUILD")[0]
        srcs = [f"{prefix}{src}" for src in match[2].split(" ")] if match[2] else []
        hdrs = [f"{prefix}{hdr}" for hdr in match[5].split(" ")] if match[5] else []
        for src in srcs:
            result[src] = f"{BUILD}:{line}"
        for hdr in hdrs:
            result[hdr] = f"{BUILD}:{line}"
    # Prepare our directory if it doesn't exist.
    os.makedirs(LOOKUP_DATA_DIR, exist_ok=True)
    # Save our file so we can potentially reuse the map for future queries.
    with open(LOOKUP_DATA_PATH, mode="w+", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2)
    return result


def get_corresponding_build_info(args):
    """Load (build if does not exist) the lookup_data map from and return corresponding BUILD file and target.

    Will rebuild the map if src file is not found in the map and file was loaded.
    """
    did_build = False
    # Try to load lookup_data.
    if os.path.isfile(LOOKUP_DATA_PATH):
        with open(LOOKUP_DATA_PATH, mode="r", encoding="utf-8") as fp:
            try:
                lookup_data = json.load(fp)
            # If we have issues loading the json file, build it.
            except json.decoder.JSONDecodeError as ex:
                lookup_data = build_lookup_data()
    # If lookup data does not exist, build it.
    else:
        lookup_data = build_lookup_data()
        did_build = True

    # If our file exists in the map, return the BUILD and target information.
    if args.input in lookup_data:
        return lookup_data[args.input]
    else:
        # If the file does not exist and we did not build, rebuild the map.
        if not did_build:
            lookup_data = build_lookup_data()
        # If the file exists in the newly built map, return the BUILD and target information.
        if args.input in lookup_data:
            return lookup_data[args.input]
    return None


def main(args):
    # Ensure our custom buildozer binary exists.
    maybe_fetch_buildozer()
    # Fetch build info.
    build_info = get_corresponding_build_info(args)
    if build_info:
        print(build_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "-i", "--input", required=True, type=str, help="Input file for which to find the corresponding BUILD file"
    )
    args = parser.parse_args()
    main(args)
