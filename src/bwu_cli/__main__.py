import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bwu_cli import cli

if __name__ == "__main__":
    cli()