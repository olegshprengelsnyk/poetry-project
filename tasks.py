import os
import shutil
import sys

from invoke import task


def remove(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


@task
def clean(c):
    c.run("pyclean .")

    name, _ = c.run("poetry version").stdout.split()

    remove(f"{name}.spec")
    remove("dist")


@task
def lint(c):
    c.run("pylint src")


@task
def build(c):
    # Clean previous build
    clean(c)

    # Create filename
    name, version = c.run("poetry version").stdout.split()
    filename = f"{name}-{version}-{sys.platform}"

    # Build exe with Pyinstaller
    c.run(
        f"python -O -m PyInstaller --clean --onefile --name {filename} -y src/main.py")


@task
def release(c):
    _, version = c.run("poetry version").stdout.split()

    c.run(f"git tag v{version}")
    c.run(f"git push origin v{version}")
