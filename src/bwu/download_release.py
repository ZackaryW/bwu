import hashlib
import os
import typing
import requests

moddir: str = os.path.dirname(__file__)


def get_releases():
    raw: typing.List[dict] = requests.get(
        "https://api.github.com/repos/Bitwarden/clients/releases"
    ).json()
    filtered = [x for x in raw if x["tag_name"].startswith("cli")]

    return filtered

def get_latest_release():
    return get_releases()[0]


def get_name():

    import platform

    if platform.system() == "Windows":
        return "bw-windows"
    elif platform.system() == "Linux":
        return "bw-linux"
    elif platform.system() == "Darwin":
        return "bw-macos"
    else:
        raise Exception("Unsupported platform")


def download_release():
    latest = get_latest_release()
    latest_tag = latest["tag_name"]
    # tag removing front cli-v
    striped_tag = latest_tag[5:]

    lfn = f"{get_name()}-{striped_tag}.zip"
    sha = f"{get_name()}-sha256-{striped_tag}.txt"
    lfn_bytes = sha_verifier = None
    for asset in latest["assets"]:
        if asset["name"] == lfn:
            lfn_bytes = requests.get(asset["browser_download_url"]).content
        if asset["name"] == sha:
            sha_verifier = requests.get(asset["browser_download_url"]).text
        if lfn_bytes and sha_verifier:
            break

    assert (
        hashlib.sha256(lfn_bytes).hexdigest() == sha_verifier.lower()
    ), "sha256 mismatch"

    with open(os.path.join(moddir, "bw"), "wb") as f:
        f.write(lfn_bytes)


def verify_current_release():
    if not os.path.exists(os.path.join(moddir, "bw")):
        return False

    latest = get_latest_release()
    latest_tag = latest["tag_name"]
    # tag removing front cli-v
    striped_tag = latest_tag[5:]

    sha = f"{get_name()}-sha256-{striped_tag}.txt"

    basehash = hashlib.sha256(open(os.path.join(moddir, "bw"), "rb").read()).hexdigest()

    assert basehash == sha.lower(), "sha256 mismatch"
