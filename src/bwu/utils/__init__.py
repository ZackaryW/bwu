from bwu.model import Proc
import subprocess


def _prep_args(proc: Proc, *args, no_session=False):
    if not proc.session and not no_session:
        raise RuntimeError("No session found.")

    cmd = [proc.path]
    if proc.session and not no_session:
        cmd += ["--session", proc.session]
    cmd += list([str(x) for x in args])

    return cmd

def send_proc(proc: Proc, *args, no_session=False, timeout=30):
    cmd = _prep_args(proc, *args, no_session=no_session)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if res.stdout and "? Master password:" in res.stdout.decode("utf-8"):
        raise RuntimeError("Master password required.")
    if res.stderr and res.stderr == b"mac failed.\n":
        raise RuntimeError("Mac Failed.")
    if res.returncode != 0:
        raise Exception(res.stderr.decode("utf-8"))
    return res.stdout.decode("utf-8").strip()
