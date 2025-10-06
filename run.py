#
# CLI Utilities for HIM FastAPI Project
#
# Usage:
#   python run.py generate-changelog --output CHANGELOG.md
#   python run.py git-commit "Commit message" --tag v1.0.0
#   python run.py run-dev
#   python run.py run-prod
#   python run.py run-prod-gunicorn
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
#   run-dev             Jalankan FastAPI dengan uvicorn (dev mode, reload)
#       Example:
#           python run.py run-dev
#
#   run-prod            Jalankan FastAPI dengan uvicorn (jumlah worker = CPU core)
#       Example:
#           python run.py run-prod
#
#   run-prod-gunicorn   Jalankan FastAPI dengan gunicorn (jumlah worker = CPU core)
#       Example:
#           python run.py run-prod-gunicorn
#

import sys
import time
import typer
import subprocess
from pathlib import Path
import os
import multiprocessing
from dotenv import load_dotenv, find_dotenv
# import uvicorn

app = typer.Typer()

# Definisikan konteks untuk menyimpan konfigurasi
class AppContext:
    def __init__(self):
        self.config = {
            "wait": False,
            "is_service": False
        }

# Buat objek konteks
ctx_obj = AppContext()

def activate_venv(venv_path: str = "venv-3.10"):
    """Aktifkan virtualenv sebelum menjalankan server"""
    venv_dir = Path(venv_path)
    if not venv_dir.exists():
        typer.echo(f"❌ Virtualenv {venv_path} tidak ditemukan.")
        raise typer.Exit(1)

    activate_script = (
        venv_dir / "Scripts" / "activate"
        if os.name == "nt"
        else venv_dir / "bin" / "activate"
    )

    if not activate_script.exists():
        typer.echo(f"❌ Script {activate_script} tidak ditemukan.")
        raise typer.Exit(1)

    typer.echo(f"✅ Script {activate_script} ditemukan.")
    os.system(f".\\{activate_script}")
    typer.echo(f"✅ Virtualenv {venv_path} telah diaktifkan.")

def load_env_file(env_file: str = None):
    """
    Memuat variabel lingkungan dari file .env
    
    Args:
        env_file (str, optional): Path ke file .env. Jika None, akan mencari file .env di direktori saat ini.
    """
    # Jika env_file ditentukan, gunakan path tersebut
    if env_file:
        if not os.path.exists(env_file):
            typer.echo(f"File .env tidak ditemukan di: {env_file}")
            raise typer.Exit(code=1)
        load_dotenv(env_file)
    else:
        # Jika env_file tidak ditentukan, cari file .env di direktori saat ini
        dotenv_path = find_dotenv()
        if not dotenv_path:
            typer.echo("File .env tidak ditemukan")
            raise typer.Exit(code=1)
        load_dotenv(dotenv_path)
    
    typer.echo(f"Berhasil memuat konfigurasi dari file {env_file}")

@app.command(help="Run FastAPI app in development mode (uvicorn reload)")
def run_dev(host: str = typer.Option("127.0.0.1", help="Host to run the app on"),
            port: int = typer.Option(8000, help="Port to run the app on"),
            reload: bool = typer.Option(True, help="Enable auto-reload")):
    """
    Jalankan FastAPI dengan uvicorn di mode development (auto-reload).
    """
    # uvicorn.run("app.main:app", host=host, port=port, reload=reload)
    # os.system(f"uvicorn app.main:app --host {host} --port {port} --reload {reload}")
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--reload" if reload else None,
    ]
    typer.echo(f"Menjalankan: {' '.join(cmd)}")
    activate_venv()
    subprocess.run(cmd)

@app.command(help="Run FastAPI app in production mode (uvicorn with workers=CPU core count)")
def run_prod(host: str = typer.Option("127.0.0.1", help="Host to run the app on"),
            port: int = typer.Option(8000, help="Port to run the app on"),
            workers: int = typer.Option(multiprocessing.cpu_count(), help="Number of workers to run")):
    """
    Jalankan FastAPI dengan uvicorn dan jumlah worker sesuai jumlah CPU core.
    """
    # uvicorn.run("app.main:app", host=host, port=port, workers=workers)
    # os.system(f"uvicorn app.main:app --host {host} --port {port} --workers {workers}")
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--workers", str(workers),
    ]
    typer.echo(f"Menjalankan: {' '.join(cmd)}")
    activate_venv()
    subprocess.run(cmd)

@app.command(help="Run FastAPI app in production mode (gunicorn with workers=CPU core count)")
def run_prod_gunicorn(host: str = typer.Option("127.0.0.1", help="Host to run the app on"),
            port: int = typer.Option(8000, help="Port to run the app on"),
            workers: int = typer.Option(multiprocessing.cpu_count(), help="Number of workers to run")):
    """
    Jalankan FastAPI dengan gunicorn dan jumlah worker sesuai jumlah CPU core.
    """
    if os.name == "nt":
        typer.echo(f"❌ gunicorn not supported on Windows, please use ./run.py run-prod instead.")
        raise typer.Exit(1)
    # os.system(f"gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind {host}:{port} --workers {workers}")
    cmd = [
        "gunicorn",
        "app.main:app",
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", f"{host}:{port}",
        "--workers", str(workers),
    ]
    typer.echo(f"Menjalankan: {' '.join(cmd)}")
    activate_venv()
    subprocess.run(cmd)

@app.command()
def generate_changelog(output: str = typer.Option("CHANGELOG.md", help="Output changelog file name")):
    """
    Generate a changelog file using git-cliff and git-cliff.toml config.
    By default, output is CHANGELOG.md.
    """
    try:
        activate_venv()
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

@app.command()
def git_commit_amend(message: str = typer.Argument(..., help="Commit message"), tag: str = typer.Option(None, help="Tag to add after commit")):
	"""Commit amend changes to git with a message and optional tag."""
	try:
		subprocess.check_call(["git", "add", "."])
		subprocess.check_call(["git", "commit", "--amend", "-m", message])
		typer.echo(f"Committed amend with message: {message}")
		if tag:
			subprocess.check_call(["git", "tag", tag])
			typer.echo(f"Tag '{tag}' added.")
	except Exception as e:
		typer.echo(f"Error during git commit/tag amend: {e}", err=True)



@app.command(help="Run Postgre Server")
def run_pg_server_windows(ctx: typer.Context, env_file: str = typer.Option(".env.pglocal", help="Env file for pgsql")):
    """
    Jalankan Postgre Server.
    """
    # Memuat variabel lingkungan
    ctx_obj.config["is_service"] = True
    load_env_file(env_file)
    # pg_drive = os.getenv("PG_DRIVE")
    pg_dir = os.getenv("PG_DIR")
    pg_data = os.getenv("PG_DATA")
    pg_log = os.getenv("PG_LOG")
    # exec_path = Path("\pgsql\bin\pg_ctl.exe")

    dir_path = Path(pg_dir)
    if not dir_path.exists():
        typer.echo(f"❌ Directory {pg_dir} tidak ditemukan.")
        raise typer.Exit(1)
    
    exec_path = Path((pg_dir + "\\pgsql\\bin\\pg_ctl.exe"))
    if not exec_path.exists():
        typer.echo(f"❌ Executable {exec_path} tidak ditemukan.")
        raise typer.Exit(1)
    
    data_path = dir_path / pg_data
    if not data_path.exists():
        typer.echo(f"❌ Directory {pg_data} tidak ditemukan.")
        raise typer.Exit(1)
    
    log_path = dir_path / pg_log
    if not log_path.exists():
        typer.echo(f"❌ Directory {pg_log} tidak ditemukan.")
        raise typer.Exit(1)

    cmd = [
        exec_path.as_posix(),
        "-D",
        data_path.as_posix(),
        "-l",
        log_path.as_posix(),
        "start"
    ]
    typer.echo(f"Menjalankan: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    ctx.exit(0)  # Exit dengan kode 0 (sukses)

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
    finally:
        if ctx_obj.config["is_service"]:
            typer.echo("👉 Service berjalan.")
        else:
            if ctx_obj.config["wait"]:
                input("👉 Tekan Enter untuk keluar...")
            else:
                wait = 3
                typer.echo(f"Exiting in {wait}s...")
                time.sleep(wait)
            # if os.name == "nt":
            #     input("👉 Tekan Enter untuk keluar...")
            sys.exit(0)
