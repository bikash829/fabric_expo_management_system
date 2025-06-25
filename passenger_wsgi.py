import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"

from fabric_expo_management_system.wsgi import application