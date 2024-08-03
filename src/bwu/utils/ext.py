from bwu.ext import os_keyring
from bwu.model import Proc
import os


def set_keyring(proc: Proc):
    os_keyring().set_password("bwu", proc.path, proc.session)


def set_environ(proc: Proc):
    os.environ["BWU_SESSION"] = proc.session


def fetch_session(proc: Proc):
    if not proc.session and "BWU_SESSION" in os.environ:
        object.__setattr__(proc, "session", os.environ["BWU_SESSION"])

    if not proc.session:
        try:
            ps = os_keyring().get_password("bwu", proc.path)
            if ps:
                object.__setattr__(proc, "session", ps)
        except:  # noqa
            pass
            