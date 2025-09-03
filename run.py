#
# CLI Utilities for HIM FastAPI Project
#
# Usage:
#   python run.py generate-changelog --output CHANGELOG.md
#   python run.py git-commit "Commit message" --tag v1.0.0
#
# Commands:
#   generate-changelog   Generate changelog file from git commit history.
#       --output         (optional) Output changelog file name (default: CHANGELOG.md)
#       Example:
#           python run.py generate-changelog
#           python run.py generate-changelog --output custom_changelog.md
#
#   git-commit          Commit all changes to git with a commit message and optional tag.
#       <message>        Commit message (required)
#       --tag            (optional) Tag to add after commit
#       Example:
#           python run.py git-commit "Initial commit"
#           python run.py git-commit "Release v1.0.0" --tag v1.0.0
#
# Note: Ensure you have git installed and configured.

import typer
import subprocess
from pathlib import Path

app = typer.Typer()

@app.command()
def generate_changelog(output: str = typer.Option("CHANGELOG.md", help="Output changelog file name")):
    """
    Generate a changelog file using git-cliff and git-cliff.toml config.
    By default, output is CHANGELOG.md.
    """
    try:
        subprocess.check_call([
            "git-cliff",
            "-c", "git-cliff.toml",
            "-o", output
        ])
        typer.echo(f"Changelog generated at {output} using git-cliff.")
    except Exception as e:
        typer.echo(f"Error generating changelog with git-cliff: {e}", err=True)

@app.command()
def git_commit(message: str = typer.Argument(..., help="Commit message"), tag: str = typer.Option(None, help="Tag to add after commit")):
	"""Commit changes to git with a message and optional tag."""
	try:
		subprocess.check_call(["git", "add", "."])
		subprocess.check_call(["git", "commit", "-m", message])
		typer.echo(f"Committed with message: {message}")
		if tag:
			subprocess.check_call(["git", "tag", tag])
			typer.echo(f"Tag '{tag}' added.")
	except Exception as e:
		typer.echo(f"Error during git commit/tag: {e}", err=True)

if __name__ == "__main__":
	app()
