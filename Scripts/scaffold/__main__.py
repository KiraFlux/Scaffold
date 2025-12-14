"""Scaffold Project Python script"""

import sys
from pathlib import Path

from scaffold import Config
from scaffold import Project
from scaffold._cli import CleanupCommandRunner
from scaffold._cli import CommandLineInterface
from scaffold._cli import DisplayModelCommandRunner


def _start():
    cli = CommandLineInterface((
        CleanupCommandRunner,
        DisplayModelCommandRunner,
    ))

    args = cli.parse_args(None)
    command_runner = cli.get(args.mode).create(args)

    try:
        config_default = Config.default(Path(args.root_directory).resolve())
        project = Project(config_default)
        command_runner.run(project)

    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)


_start()
