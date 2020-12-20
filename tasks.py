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

    remove("PROJECT_NAME.spec")
    remove("dist")


@task
def lint(c):
    c.run("pylint src")


@task
def build(c):
    # Clean previous build
    clean(c)

    # Create filename
    version = c.run("poetry version -s").stdout
    filename = f"PROJECT_NAME-{version}-{sys.platform}"

    # Build exe with Pyinstaller
    c.run(
        f"python -O -m PyInstaller --clean --onefile --name {filename} -y src/main.py")


@task
def release(c):
    version = c.run("poetry version -s").stdout

    c.run(f"git tag v{version}")
    c.run(f"git push origin v{version}")
