from bwu.model import Proc
from bwu.utils import send_proc


def unlock(proc: Proc, password: str) -> str:
    """Unlock the account with the given password."""
    res = send_proc(proc, "unlock", password, "--raw", no_session=True)
    if "Invalid master password." in res:
        return None
    return res.strip()


def terminal_unlock(proc: Proc):
    import click

    password = click.prompt("Enter your Bitwarden password", hide_input=True)
    return unlock(proc, password)


def set_session(proc: Proc, password: str = None, session: str = None):
    if session:
        return Proc(proc.path, session=session)

    if password:
        p = unlock(proc, password)
    else:
        p = terminal_unlock(proc)

    if not p:
        raise Exception("Invalid password")
    return Proc(proc.path, session=p)
