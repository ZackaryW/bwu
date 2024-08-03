
from itertools import product
import platform
from functools import cache
import typing
import pathvalidate
import functools
import io
import zipfile
import requests
import hashlib
import os
import time

@cache
def os_keyring():
    """
    Returns an instance of the appropriate keyring backend based on the current operating system.

    This function uses the `platform.system()` function to determine the current operating system and then imports the appropriate keyring backend module. The following keyring backends are supported:
    - Windows: `keyring.backends.Windows.WinVaultKeyring`
    - macOS: `keyring.backends.macOS.Keyring`
    - Linux: `keyring.backends.SecretService.Keyring`

    The function is decorated with `@cache`, which means that the result of the first call to `os_keyring()` is cached and subsequent calls will return the cached result.

    Returns:
        An instance of the appropriate keyring backend.
    """
    if platform.system() == "Windows":
        from keyring.backends.Windows import WinVaultKeyring

        return WinVaultKeyring()
    elif platform.system() == "Darwin":
        from keyring.backends.macOS import Keyring

        return Keyring()
    elif platform.system() == "Linux":
        from keyring.backends.SecretService import Keyring

        return Keyring()


def generate_combinations(**kwargs):
    if not kwargs:
        return [{}]
    # Separate the keys and values
    keys, values = zip(*kwargs.items())

    # Generate all combinations where lists are expanded
    value_combinations = product(*(v if isinstance(v, list) else [v] for v in values))

    # Convert combinations back to a list of dictionaries
    result = [dict(zip(keys, combination)) for combination in value_combinations]
    return result


#

# name dict
def _format_via_id_name_method(new_dict: dict, santize_key: str, entry: dict, key: str):
    if key in new_dict:
        raise ValueError(f"Duplicate key: {key}")

    sanitized = pathvalidate.sanitize_filename(entry[santize_key])

    if sanitized in new_dict.values():
        sanitized = f"{sanitized} [{key[-6:]}]"

    new_dict[key] = sanitized


def generate_namedict(
    entries: typing.Dict[str, dict],
    santize_key: str,
    filters: typing.List[typing.Callable] = [],
    format_method: typing.Callable = _format_via_id_name_method,
):
    name_dict = {}

    for key, entry in entries.items():
        for filter_func in filters:
            if not filter_func(entry):
                continue

        format_method(name_dict, santize_key, entry, key)

    return name_dict

# SECTION
# release ensure

@cache
def get_release_name():
    if platform.system() == "Windows":
        return "bw-windows"
    elif platform.system() == "Linux":
        return "bw-linux"
    elif platform.system() == "Darwin":
        return "bw-macos"
    else:
        raise Exception("Unsupported platform")


@cache
def get_cli_releases_info():
    raw: typing.List[dict] = requests.get(
        "https://api.github.com/repos/Bitwarden/clients/releases"
    ).json()
    filtered = [x for x in raw if x["tag_name"].startswith("cli")]
    return filtered


def get_latest_release_info():
    return get_cli_releases_info()[0]


def download_cli_release(path: str):
    latest = get_latest_release_info()

    latest_tag = latest["tag_name"]
    # tag removing front cli-v
    striped_tag = latest_tag[5:]

    lfn = f"{get_release_name()}-{striped_tag}.zip"
    sha = f"{get_release_name()}-sha256-{striped_tag}.txt"
    lfn_bytes = sha_verifier = None
    for asset in latest["assets"]:
        if asset["name"] == lfn:
            lfn_bytes = requests.get(asset["browser_download_url"]).content
        if asset["name"] == sha:
            sha_verifier = requests.get(asset["browser_download_url"]).text
        if lfn_bytes and sha_verifier:
            break
    # extract lfn zip
    # get internal file bytes
    lfn_file = io.BytesIO(lfn_bytes)

    zipf = zipfile.ZipFile(lfn_file, "r")
    internalfile = zipf.open(zipf.namelist()[0])
    content_bytes = internalfile.read()
    zipf.close()

    new_sha = hashlib.sha256(lfn_bytes).hexdigest()
    assert new_sha == sha_verifier.strip().lower(), "sha256 mismatch"

    savepath = os.path.join(path, "bw")

    with open(savepath, "wb") as f:
        f.write(content_bytes)


def verify_cli_release_latest(curr_ver):
    latest = get_latest_release_info()
    latest_tag = latest["tag_name"]
    striped_tag = latest_tag[5:]

    return curr_ver == striped_tag



class timed_cache:
    def __init__(self, ttl=10):
        self.ttl = ttl
        self.cache = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Creating a unique key based on function arguments and keyword arguments
            key = (args, frozenset(kwargs.items()))
            current_time = time.time()

            # Check if we have a valid cached value
            if key in self.cache and current_time < self.cache[key]["expire_time"]:
                return self.cache[key]["value"]

            # Call the function and cache the result
            result = func(*args, **kwargs)
            self.cache[key] = {"value": result, "expire_time": current_time + self.ttl}
            return result

        return wrapped
