import sys
import os

# Add project directory to sys.path
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["OPENBLAS_NUM_THREADS"] = "1"

from fabric_expo_management_system.wsgi import application