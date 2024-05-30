import subprocess
from time import sleep
import click
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from bwu.base_proc import BWU

@click.group(chain=True)
def cli():
    pass

@cli.command()
@click.option("--display-session", "-ds", is_flag=True)
def unlock( display_session=False):
    password = click.prompt("Password", hide_input=True)
    res = BWU.proc("unlock", password, "--raw")

    if display_session:
        print(res)
    BWU._SESSION = res

@cli.command(help="Set session/path")
@click.argument("arg")
def set(arg :str):
    click.echo("Checking validity...", nl=False)
    if arg.endswith("=="):
        BWU._SESSION = arg
    elif os.path.exists(arg) or subprocess.run([arg, "--version"], stdout=None, stderr=None).returncode == 0:
        BWU._PATH = arg
    sleep(2)
    click.echo("OK")
@cli.command()
@click.argument("args")
def proc(args):
    print(BWU.proc(*args.split()))

@cli.command(help="Download all attachments")
@click.option("--path", "-p", type=click.Path(), default=os.path.join(os.getcwd(), "export"))
@click.option("--save-entry", "-s", is_flag=True, help="Save additional data about entry")
def downfiles(path, save_entry):
    from bwu.download_attachments import DownloadAttachments
    DownloadAttachments.downloadAttachments(path, save_entry)

def main():
    try:
        cli()
    except Exception as e:
        click.echo(e)

if __name__ == "__main__":
    main()