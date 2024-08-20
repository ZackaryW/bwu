import json
import typing

import pathvalidate
from bwu.model import BwEntry
from bwu.ext import generate_combinations
from bwu.model import Proc
from bwu.utils import send_proc


def version(proc: Proc):
    return send_proc(proc, "--version", no_session=True)


def status(proc: Proc):
    res = send_proc(proc, "status", no_session=True)
    return json.loads(res)


def is_logged(proc: Proc):
    return status(proc).get("status", None) not in ["locked", "unauthenticated"]


def lock(proc: Proc):
    return send_proc(proc, "lock", no_session=True)


def list_items(
    proc: Proc,
    url=None,
    folderid=None,
    collectionid=None,
    organizationid=None,
    search= None,
    pretty: bool = False,
    limit: int = -1,
) -> typing.List[BwEntry]:
    items : typing.List[BwEntry] = []
    params = {
        "url": url,
        "folderid": folderid,
        "collectionid": collectionid,
        "organizationid": organizationid,
        "search": search,
    }
    params = {k: v for k, v in params.items() if v is not None}
    for combination in generate_combinations(**params):
        cmd = ["list", "items"]
        for k, v in combination.items():
            cmd.append(f"--{k}")
            cmd.append(str(v))

        if pretty:
            cmd.append("--pretty")
        res = send_proc(proc, *cmd)
        data : typing.List[BwEntry] = json.loads(res)

        items.extend(data)

        # clear duplicates
        items_id = []
        for i in range(len(items) - 1, -1, -1):
            if items[i]["id"] in items_id:
                del items[i]
            else:
                items_id.append(items[i]["id"]) 


        if limit > 0 and len(items) >= limit:
            items = items[:limit]
            break

    for item in items:
        item["sanitized_name"] = pathvalidate.sanitize_filename(item["name"])

    return items


def dict_items(
    proc: Proc,
    url=None,
    folderid=None,
    collectionid=None,
    organizationid=None,
    search=None,
    primary_key: str = "id",
    pretty: bool = False,
    limit: int = -1,
) -> typing.Dict[str, BwEntry]:
    items = {}
    params = {
        "url": url,
        "folderid": folderid,
        "collectionid": collectionid,
        "organizationid": organizationid,
        "search": search,
    }
    params = {k: v for k, v in params.items() if v is not None}
    for combination in generate_combinations(**params):
        cmd = ["list", "items"]
        for k, v in combination.items():
            cmd.append(f"--{k}")
            cmd.append(str(v))

        if pretty:
            cmd.append("--pretty")
        res = send_proc(proc, *cmd)
        data = json.loads(res)

        items.update({item[primary_key]: item for item in data})

        if limit > 0 and len(items) >= limit:

            items = {k: v for i, (k, v) in enumerate(items.items()) if i < limit}
            break

    for item in items.values():
        item["sanitized_name"] = pathvalidate.sanitize_filename(item["name"])

    return items

def with_attachments(items : dict |list):
    if isinstance(items, dict):
        return {k: v for k, v in items.items() if v.get("attachments", None) is not None}
    else:
        return [v for v in items if v.get("attachments", None) is not None]
