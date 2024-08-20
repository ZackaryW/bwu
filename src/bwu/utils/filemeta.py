import json
import math
import os
import typing
from bwu.model import BwEntry

def create_attachments_meta(entry : BwEntry, meta : dict = {}):
    meta = {"entries" : {}, "id" : entry["id"]}
    exclude = meta.get("exclude", [])
    for attachment in entry["attachments"]:
        if attachment["fileName"] in exclude:
            continue

        meta["entries"][attachment["fileName"]] = math.floor(int(attachment["size"])/1024)

    return meta

def get_file_meta(path : str, exclude = [], bwentry : BwEntry = None):
    meta_path = os.path.join(path, "meta.json") if not path.endswith("meta.json") else path
    folder_path = os.path.dirname(path) if "meta.json" in path else path

    if not os.path.exists(folder_path):
        return None

    meta = {"entries" : {}}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            existing_meta = json.load(f)
        meta["id"] = existing_meta["id"]
        if "exclude" in existing_meta:
            meta["exclude"] = list(set(existing_meta["exclude"]) + set(exclude))
    else:
            if bwentry:
                meta["id"] = bwentry["id"]
            meta["exclude"] = exclude
    
    for file in os.listdir(folder_path):
        if file.startswith(".") or file.startswith("_"):
            continue

        if file in meta.get("exclude", []):
            continue

        if file == "meta.json":
            continue

        meta["entries"][file] = math.floor(int(os.path.getsize(os.path.join(folder_path, file)))/1024)

    return meta


def compare_changes(bwentry : typing.Union[BwEntry, dict], path : typing.Union[str, dict], favor : typing.Literal["left", "right"] = "left"):
    changes = []

    if not isinstance(path, dict):
        path_meta = get_file_meta(path, bwentry=bwentry)
    else:
        path_meta = path

    entry_meta = create_attachments_meta(bwentry, path_meta)

    for file, size_from_entry in entry_meta.get("entries", {}).items():
        if file not in path_meta["entries"]:
            if favor == "left":
                changes.append({"file" : file, "kind" : "remove_right"})
            else:
                changes.append({"file" : file, "kind" : "use_right"})
            continue

        size_from_path = path_meta["entries"][file]
        if size_from_entry!= size_from_path:
            changes.append({"file" : file, "kind" : favor})

    for file in path_meta.get("entries", {}).keys():
        if file not in entry_meta["entries"]:
            if favor == "left":
                changes.append({"file" : file, "kind" : "use_left"})
            else:
                changes.append({"file" : file, "kind" : "remove_left"})

    return changes

def update_file_meta(path : str, am : dict):
    meta_path = os.path.join(path, "meta.json") if not path.endswith("meta.json") else path
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            existing_meta = json.load(f)
        existing_meta["entries"].update(am["entries"])
        existing_meta["exclude"] = list(set(existing_meta["exclude"]) | set(am.get("exclude", [])))
        existing_meta["id"] = am["id"]  
    else:
        existing_meta = am

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(existing_meta, f)


