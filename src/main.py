"""
This module streamlines the initial run of the project by automatically installing the required packages
"""

import subprocess
import sys

subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "-r" "../requirements.txt"]
)
from app import run_server

run_server()
