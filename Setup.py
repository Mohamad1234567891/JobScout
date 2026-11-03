"""
This file is part of JobScout, an open-source job-search and job-match
engine that scrapes LinkedIn and scores every posting against your profile.

Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.

Original JobScout repository: https://github.com/Mohamad1234567891/JobScout

Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

One-command, cross-platform setup for JobScout. Uses only the Python
standard library, so nothing needs to be installed to run it.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def run(step, command, **kwargs):
    print(f"\n=== {step} ===")
    print("$", " ".join(str(part) for part in command))
    subprocess.check_call(command, cwd=str(ROOT), **kwargs)


def venv_python():
    if os.name == "nt":
        return str(VENV / "Scripts" / "python.exe")
    return str(VENV / "bin" / "python")


def main():
    print("JobScout setup")
    print("--------------")

    # 1. Pick a Python interpreter (3.10 or newer).
    if sys.version_info < (3, 10):
        print("[!] Python 3.10 or newer is required.")
        return 1

    # 2. Create the virtual environment.
    if not VENV.exists():
        run("Creating the virtual environment .venv", [sys.executable, "-m", "venv", str(VENV)])
    else:
        print("\n=== .venv already exists - using it ===")

    python = venv_python()

    # 3. Upgrade pip inside the environment.
    run("Upgrading pip", [python, "-m", "pip", "install", "--upgrade", "pip"])

    # 4. Install all dependencies from requirements.txt.
    run("Installing the dependencies", [python, "-m", "pip", "install", "-r", "requirements.txt"])

    # 5. Install the Playwright Chromium browser used by the scraper.
    run("Installing the Playwright Chromium browser",
        [python, "-m", "playwright", "install", "chromium"])

    # 6. Verify that every dependency imports correctly.
    run("Verifying the installation",
        [python, "-c",
         "import PySide6, curl_cffi, lxml, playwright, desktop_notifier; "
         "print('All dependencies imported successfully.')"])

    print("\n=== Setup complete ===")
    print("Activate the environment and run JobScout:")
    if os.name == "nt":
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")
    print("    python cli.py GUI            # graphical interface")
    print('    python cli.py "AI Engineer"  # CLI search')
    return 0


if __name__ == "__main__":
    sys.exit(main())
