import hashlib
import json
import os
import subprocess

moddir: str = os.path.dirname(__file__)

class BWU:
    _SESSION: str = os.environ.get("BWU_SESSION", None)
    _PATH: str = os.environ.get("BWU_PATH", os.path.join(moddir, "bw"))
    _HASH : str

    @classmethod
    def __prep_args(cls, *args):
        cmd = [cls._PATH]
        if cls._SESSION:
            cmd += ["--session", cls._SESSION]
        cmd += list([str(x) for x in args])
        
        return cmd

    @classmethod
    def proc(cls, *args):
        res = subprocess.run(
            cls.__prep_args(*args), 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
        )
        if res.returncode != 0:
            raise Exception(res.stderr.decode("utf-8"))
        return res.stdout.decode("utf-8").strip()
        

class _BWUsets:
    @property
    def version(self):
        return BWU.proc("--version")
    
    @property
    def status(self):
        raw = BWU.proc("status")
        return json.loads(raw)
    
    @property
    def unlocked(self):
        return self.status["status"] not in ["locked", "unauthenticated"]
    
    @property
    def need_login(self):
        return self.status["status"] == "unauthenticated"
    
    def lock(self):
        return BWU.proc("lock")

    def unlock(self, password: str):
        return BWU.proc("unlock", password)

BWUSet = _BWUsets()

if not os.path.exists(BWU._PATH):
    raise Exception("bw not found. Is it installed?")
BWU._HASH = hashlib.sha256(open(os.path.join(moddir, "bw"), "rb").read()).hexdigest()

if BWU._PATH == os.path.join(moddir, "bw"):
    # create tempdir
    import tempfile
    import zipfile

    # extract zip to tempdir
    tdir = tempfile.TemporaryDirectory().name
    with zipfile.ZipFile(os.path.join(moddir, "bw"), "r") as zip_ref:
        zip_ref.extractall(tdir)

    # set BWU_PATH
    BWU._PATH = os.path.join(tdir, "bw")

    # run bw --version to check how new it is
    currentVer = subprocess.run(
        [BWU._PATH, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if currentVer.returncode != 0:
        raise Exception("bw not found. Is it installed?")

    # check if the current version is new enough
    currentVer = currentVer.stdout.decode("utf-8").strip()

    print(f"Current version: {currentVer}")

    # check against current year and month
    import datetime

    splitted = currentVer.split(".")
    asdate = datetime.date(int(splitted[0]), int(splitted[1]), int(splitted[2]))

    curr = datetime.datetime.now().date()

    if asdate - datetime.timedelta(days=30) > curr:
        raise Exception("Newer version of bw is required. Please update.")

