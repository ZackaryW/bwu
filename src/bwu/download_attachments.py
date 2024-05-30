import json
import os
from typing import TypedDict
import typing
from slugify import slugify
from bwu.base_proc import BWU

class Attachment(TypedDict):
    id : str
    fileName : str
    size : int
    sizeName : str
    url : str

class Entry(TypedDict):
    id : str
    organizationId : str
    folderId : str
    type : int
    reprompt : int
    name : str
    notes : str
    favorite : bool = False
    fields : typing.List[dict]
    login : dict 
    collectionIds : typing.List[str] 
    revisionDate : str
    creationDate : str
    deletedDate : typing.Optional[str] 
    attachments : typing.Optional[typing.List[Attachment]]

class DownloadAttachments:
    @staticmethod
    def entriesWithAttachments():
        res =BWU.proc("list", "items", "--pretty")
        data = json.loads(res)
        for item in data:
            item : dict
            if "attachments" in item:
                yield item

    @staticmethod
    def downloadSingleAttachment(itemid : str, filename : str, targetdir : str):
        BWU.proc(
            "get",
            "attachment", filename,
            "--itemid", itemid,
            "--output", os.path.join(targetdir, filename)
        )

    @staticmethod
    def downloadEntryAttachments(entry : Entry, targetdir : str, saveEntry : bool = False):
        subfoldername = f"[{entry["id"][-3:]}] {slugify(entry["name"])}"
        subfolder = os.path.join(targetdir, subfoldername)
        os.makedirs(subfolder, exist_ok=True)
    
        for attachment in entry["attachments"]:
            print(f"Attachment: {attachment['fileName']} ({attachment['sizeName']})")
            DownloadAttachments.downloadSingleAttachment(entry["id"], attachment["fileName"], subfolder)

        if saveEntry:
            with open(os.path.join(subfolder, "entry.bwu"), "w") as f:
                json.dump(entry, f, indent=4)
        else:
            with open(os.path.join(subfolder, "entry.bwu"), "w") as f:
                json.dump(
                    {
                        "name": entry["name"],
                        "id" : entry["id"],
                        "attachments": entry["attachments"]
                    },
                    f,
                    indent=4
                )
        

    @staticmethod
    def downloadAttachments(targetdir : str, saveEntry : bool = False):
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)

        for item in DownloadAttachments.entriesWithAttachments():
            print(f"Item: {item['name']}")
            DownloadAttachments.downloadEntryAttachments(item, targetdir, saveEntry)