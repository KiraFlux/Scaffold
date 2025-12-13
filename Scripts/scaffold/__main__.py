"""Scaffold Project Python script"""

import sys
from pathlib import Path

from scaffold.cli import CleanupCommandRunner
from scaffold.cli import CommandLineInterface
from scaffold.cli import DisplayModelCommandRunner
from scaffold.config import Config
from scaffold.project import Project


def _start():
    cli = CommandLineInterface((
        CleanupCommandRunner,
        DisplayModelCommandRunner,
    ))

    args = cli.parse_args(None)
    command_runner = cli.get(args.mode).create(args)

    try:
        command_runner.run(Project(Config.default(Path(args.root_directory).resolve())))

    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)


_start()
