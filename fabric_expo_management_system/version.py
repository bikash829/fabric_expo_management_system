import subprocess
import re

def get_git_version():
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"],
            # ["git", "tag"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        # Keep only the main tag, drop -3-gabc1234
        version = re.split(r"-", version)[0]
        
        return version
    except Exception:
        return "v0.0.0"

__version__ = get_git_version()
