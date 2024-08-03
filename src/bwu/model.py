from dataclasses import dataclass
import os
import typing


@dataclass(frozen=True)
class Proc:
    path: str
    session: str = None

    def __post_init__(self):
        if not os.path.exists(self.path) and self.path != "bw":
            raise ValueError(f"Path {self.path} does not exist")

        object.__setattr__(self, "path", os.path.abspath(self.path) if self.path != "bw" else "bw")
        
        from bwu.utils.ext import fetch_session
        fetch_session(self)


# model for bw entries
class BwAttachement(typing.TypedDict, total=False):
    id: str
    fileName: str
    size: int
    sizeName: str
    url: str


class BwEntry(typing.TypedDict, total=False):
    id: str
    organizationId: str
    folderId: str
    type: int
    reprompt: int
    name: str
    sanitized_name: str
    notes: str
    favorite: bool = False
    fields: typing.List[dict]
    login: dict
    collectionIds: typing.List[str]
    revisionDate: str
    creationDate: str
    deletedDate: typing.Optional[str]
    attachments: typing.Optional[typing.List[BwAttachement]]
