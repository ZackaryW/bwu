import json
import pprint
import click

from bwu.model import Proc
from bwu.utils.account import set_session
from bwu.utils.ext import fetch_session, set_environ
from bwu.utils.file import download_all_attachments
from bwu.utils import send_proc

proc : Proc = Proc("bw")
fetch_session(proc)

@click.group(chain=True)
def cli():
    pass

@cli.command("auth", help="authenticate")
@click.option("--session", "-s", default=None)
@click.option("--password", "-p", default=None)
@click.option("--no-keyring", "-nk", is_flag=True)
@click.option("--use-environ", "-e", is_flag=True)
def sess(session, password, no_keyring, use_environ):
    global proc
    set_session(proc, session=session, password=password)
    if not no_keyring:
        from bwu.utils.ext import set_keyring
        set_keyring(proc)
    
    if use_environ:
        set_environ(proc)

@cli.command("set-path", help="set path")
@click.argument("path", required=False)
def set_path(path= "bw"):
    global proc
    proc = Proc(path, proc.session if proc else None)

@cli.command("downall", help="Download all entries with attachments")   
@click.option("--path", "-p")
def downall(path):
    global proc
    download_all_attachments(proc, path)

@cli.command("cmd", help="console exec")
@click.argument("cmd", nargs=-1)
@click.option("--no-session", "-ns", is_flag=True)
def cmd(cmd, no_session):
    global proc
    res = send_proc(proc, *cmd, no_session=no_session)
    try:
        click.echo(pprint.pformat(json.loads(res),indent=2))
    except: # noqa
        click.echo(res)
