import subprocess

def get_git_version():
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return version
    except Exception:
        return "unknown"

__version__ = get_git_version()
