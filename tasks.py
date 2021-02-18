import contextlib
import os
import platform
import shutil
import sys
from pathlib import Path

from invoke import call, task
from invoke.context import Context
from invoke.runners import Result

ROOT = Path(__file__).parent


def _run(c: Context, command: str) -> Result:
    return c.run(command, pty=platform.system() != "Windows")


@task
def clean_build(c):
    """Clean up build"""
    version = _run(c, "poetry version -s").stdout.rstrip()

    with contextlib.suppress(FileNotFoundError):
        os.remove(ROOT / f"PROJECT_NAME-{version}-{sys.platform}.spec")
    shutil.rmtree(ROOT / "build", ignore_errors=True)
    shutil.rmtree(ROOT / "dist", ignore_errors=True)


@task
def clean_python(c):
    """Clean up python file artifacts"""
    _run(c, f"pyclean {ROOT}")


@task
def clean_type_checking(c):
    """Clean up files from type-checking"""
    shutil.rmtree(ROOT / ".mypy_cache", ignore_errors=True)


@task(pre=[clean_build, clean_python, clean_type_checking])
def clean(c):
    """Run all clean sub-tasks"""


@task(name="format", help={"check": "Checks if source is formatted without applying changes"})
def format_(c, check=False):
    """Format code"""
    isort_options = ["--check-only", "--diff"] if check else []
    _run(c, f"isort {ROOT / 'src'} {' '.join(isort_options)}")
    black_options = ["--diff", "--check"] if check else ["--quiet"]
    _run(c, f"black {ROOT / 'src'} {' '.join(black_options)}")


@task
def type_check(c):
    """Run type-checking"""
    _run(c, f"mypy {ROOT / 'src'} --ignore-missing-imports")


@task(pre=[call(format_, check=True), type_check])
def lint(c):
    """Run all linting"""
    _run(c, f"flake8 {ROOT / 'src'} --max-line-length 119 --extend-ignore E203,W503")


@task(pre=[clean_build])
def build(c):
    """Build project distributable"""
    version = _run(c, "poetry version -s").stdout.rstrip()
    filename = f"PROJECT_NAME-{version}-{sys.platform}"

    _run(c, f"python -O -m PyInstaller --clean --onefile --name {filename} -y src/main.py")


@task
def tag(c):
    """Create GitHub tag"""
    version = _run(c, "poetry version -s").stdout.rstrip()

    _run(c, f"git tag v{version}")
    _run(c, f"git push origin v{version}")


@task
def release(c):
    """Create GitHub release"""
    version = _run(c, "poetry version -s").stdout.rstrip()

    _run(c, f'gh release create v{version} -t "PROJECT_NAME v{version}"')


@task
def upload(c):
    """Upload build as GitHub release"""
    version = _run(c, "poetry version -s").stdout.rstrip()
    filename = next(Path("dist").iterdir()).name

    _run(c, f"gh release upload v{version} dist/{filename}")
