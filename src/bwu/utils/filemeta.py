

from hashlib import sha1
import json
import math
import os
import typing
from bwu.model import BwEntry

def create_attachments_meta(object : typing.Union[str, BwEntry]):
    """
    Generate metadata for attachments from a directory path or a dictionary object.
    
    Parameters:
    - obj: A directory path (str) or a dictionary containing attachment details.
    
    Returns:
    - A dictionary where keys are filenames and values are file sizes in kilobytes.
    """
    if isinstance(object, dict):
        attachments = object.get("attachments", [])
        
        attachments_meta = {
            x["fileName"] : math.floor(int(x["size"])/1024) for x in attachments
        }

    else:
        attachments_meta = {}
        os.makedirs(object, exist_ok=True)
        for file in os.listdir(object):
            if file == "meta.json":
                continue

            if file.startswith(".") or file.startswith("_"):
                continue
            
            attachments_meta[file] = math.floor(os.path.getsize(os.path.join(object, file))/1024)

    return attachments_meta

def create_file_meta(path : str, am : typing.Dict[str, int], id : str):
    meta = {
        "id" : id,
        "hash" : sha1(json.dumps(am)).hexdigest(),
        "count" : len(am),
        "size" : sum(am.values())
    }
    with open(os.path.join(path, "meta.json"), "w") as f:
        json.dump(meta, f, indent=4)


def compare_changes(bwentry: typing.Union[BwEntry, dict], path : typing.Union[str, dict], last_sync_timestamp : float = None):
    if not isinstance(bwentry, dict):
        bwentry_meta = create_attachments_meta(bwentry)
    else:
        bwentry_meta = create_attachments_meta(bwentry)

    if not isinstance(path, dict):
        path_meta = create_attachments_meta(path)
    else:
        path_meta = create_attachments_meta(path)

    changes = []

    # Identify changed files
    for file, size_bwentry in bwentry_meta.items():
        size_path = path_meta.get(file)
        
        if size_path is None:
            # File is created in bwentry
            changes.append({"fileName": file, "change": "created"})
        elif size_bwentry != size_path:
            # File is modified
            changes.append({"fileName": file, "change": "modified"})

    # Identify deleted files
    for file in path_meta:
        if file not in bwentry_meta:
            changes.append({"fileName": file, "change": "deleted"})

    return changes