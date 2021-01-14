import os
import shutil
import sys
from pathlib import Path

from invoke import task


def remove(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


@task
def clean(c):
    c.run("pyclean .")

    version = c.run("poetry version -s").stdout.rstrip()
    filename = f"PROJECT_NAME-{version}-{sys.platform}"

    remove(f"{filename}.spec")
    remove("build")
    remove("dist")


@task
def format(c):
    c.run("black src --line-length 119")


@task
def lint(c):
    c.run("flake8 src --max-line-length 119 --extend-ignore E203")


@task
def type_check(c):
    c.run("mypy src --ignore-missing-imports")


@task
def build(c):
    # Clean previous build
    clean(c)

    # Build filename
    version = c.run("poetry version -s").stdout.rstrip()
    filename = f"PROJECT_NAME-{version}-{sys.platform}"

    print(filename)

    # Build exe with Pyinstaller
    c.run(f"python -O -m PyInstaller --clean --onefile --name {filename} -y src/main.py")


@task
def tag(c):
    version = c.run("poetry version -s").stdout.rstrip()

    c.run(f"git tag v{version}")
    c.run(f"git push origin v{version}")


@task
def release(c):
    # Get version
    version = c.run("poetry version -s").stdout.rstrip()

    # Create release
    c.run(f"gh release create v{version} -t 'PROJECT_NAME v{version}'")


@task
def upload(c):
    # Build filename
    version = c.run("poetry version -s").stdout.rstrip()
    filename = next(Path("dist").iterdir()).name

    # Upload release
    c.run(f"gh release upload v{version} dist/{filename}")
