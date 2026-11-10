"""Capture installed package versions without environment variables or credentials."""
from importlib.metadata import distributions
import platform
import subprocess


def runtime_metadata():
    return {
        "python": platform.python_version(),
        "packages": {package.metadata["Name"]: package.version for package in distributions()
                     if package.metadata["Name"]},
        "repository_revision": subprocess.check_output(
            ["git", "-C", "/tmp/ludus_scacchi", "rev-parse", "HEAD"], text=True
        ).strip(),
    }


def save_worker_requirements(runtime, path):
    """Save exact key library pins for the observed runtime."""
    names = ("tensorflow", "keras", "numpy", "mlflow", "chess", "pandas")
    lines = [f"{name}=={runtime['packages'][name]}" for name in names
             if name in runtime["packages"]]
    path.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
