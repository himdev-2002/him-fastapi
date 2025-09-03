import typer
import subprocess
from pathlib import Path

app = typer.Typer()

@app.command()
def generate_changelog(output: str = "CHANGELOG.md"):
    """Generate changelog file from git commit history."""
    try:
        # Get commit log
        log = subprocess.check_output([
            "git", "log", "--pretty=format:%h %ad %s", "--date=short"
        ], encoding="utf-8")
        changelog_path = Path(output)
        changelog_path.write_text(f"# Changelog\n\n{log}\n")
        typer.echo(f"Changelog generated at {output}")
    except Exception as e:
        typer.echo(f"Error generating changelog: {e}", err=True)

if __name__ == "__main__":
    app()
