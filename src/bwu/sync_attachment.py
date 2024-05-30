"""
This file is WIP
"""

import os
from bwu.download_attachments import DownloadAttachments, Entry
from slugify import slugify

class SyncAttachment:

    @staticmethod
    def syncEntry(entry : Entry, target_entrydir : str, saveEntry : bool = False):
        pass

    @staticmethod
    def syncAttachments(targetdir : str, saveEntry : bool = False):
        if not os.path.exists(targetdir):
            return DownloadAttachments.downloadAttachments(targetdir, saveEntry)
        
        currentFolders = os.listdir(targetdir)
        for item in DownloadAttachments.entriesWithAttachments():
            shouldbeFolder = f"[{item['id'][-3:]}] {slugify(item['name'])}"

            if not os.path.exists(os.path.join(targetdir, shouldbeFolder)):
                print(f"New folder: {shouldbeFolder}")
                DownloadAttachments.downloadEntryAttachments(item, targetdir, saveEntry)
                continue

