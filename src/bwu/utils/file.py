from genericpath import isdir
import os
from bwu.ext import generate_namedict
from bwu.model import BwEntry, Proc
from bwu.utils import send_proc
from bwu.utils.basic import dict_items

from bwu.utils.filemeta import create_attachments_meta, update_file_meta

def download_attachment(proc: Proc, attachment_id: str, item_id: str, output_path: str):
    """Download an attachment from a process."""
    send_proc(
        proc,
        "get",
        "attachment",
        attachment_id,
        "--itemid",
        item_id,
        "--output",
        output_path,
        timeout=240
    )


def upload_attachment(proc: Proc, item_id: str, file_path: str):
    """Upload an attachment to a process."""

    send_proc(proc, "create", "attachment", "--file", file_path, "--itemid", item_id)


def download_all_attachments(
    proc : Proc,
    path : str,
    filters : dict = {},
):

    entries = dict_items(proc, **filters)
    entries = {k : v for k, v in entries.items() if "attachments"in v}

    name_dict = generate_namedict(entries, )

    os.makedirs(path, exist_ok=True)

    for entryid, entry in entries.items():
        print(f"Processing Entry {entry["name"]}")
        entryname = name_dict[entryid]
        entrypath = os.path.join(path, entryname)

        os.makedirs(entrypath, exist_ok=True)
        for attachment in entry["attachments"]:
            print(f"Downloading {attachment['fileName']}")
            download_attachment(proc, attachment["id"], entryid, os.path.join(entrypath, attachment["fileName"]))

        am = create_attachments_meta(entry)
        update_file_meta(entrypath, am)

def remove_attachment(proc: Proc, attachment_id: str, item_id: str):
    """Remove an attachment from a process."""
    send_proc(
        proc,
        "delete",
        "attachment",
        attachment_id,
        "--itemid",
        item_id,
    )

def clear_attachments(proc : Proc, bwentry : BwEntry):
    if "attachments" not in bwentry:
        return
    
    for attachment in bwentry["attachments"]:
        remove_attachment(proc, attachment["id"], bwentry["id"])
