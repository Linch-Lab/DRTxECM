# Installing DRTxECM on Windows

> **Easiest route:** download `DRTxECM-python.zip` from the
> [latest release](https://github.com/Linch-Lab/DRTxECM/releases/latest), unzip it
> and double-click **`START-HERE.bat`**. The launcher finds Python, creates a
> private environment, installs everything and starts the program. The manual
> steps below are for people who prefer to do it themselves.

## Requirements

| | |
|---|---|
| Python | **3.10 or 3.11** (see the note below) |
| Disk | about 1 GB for the libraries |
| Network | only for the initial install |

**Why 3.10 and not the newest Python?** The libraries are pinned to versions
that predate Python 3.12: `scipy==1.10.0`, `numpy==1.24.1`, `pandas==1.5.3`.
None of them publish wheels for 3.12 or newer, so `pip` would try to compile
them from source, which almost always fails on Windows. If you already have a
newer Python installed you do **not** need to remove it — 3.10 can sit beside it.

## Quick Install

1. Install **Python 3.10** from
   https://www.python.org/downloads/release/python-31011/
   and tick **"Add python.exe to PATH"** during setup.
2. Open **Command Prompt** (Win+R → `cmd`).
3. Run:

```bat
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python launch.py
```

A virtual environment (`.venv`) is recommended: it needs no administrator
rights and does not touch your other Python installations.

If you prefer to install into your own environment, the equivalent is:

```bat
pip install -r requirements.txt
python launch.py
```

> `requirements.txt` includes **click**, which is easy to overlook but required:
> `pyDRTtools/__init__.py` imports `pyDRTtools.cli`, and `cli.py` imports `click`.
> Installing the other packages without it gives a `ModuleNotFoundError: click`
> at startup.

## No Git? Download ZIP

1. https://github.com/Linch-Lab/DRTxECM → **Code → Download ZIP**
2. Extract it anywhere, then open Command Prompt in that folder
3. Run the same three commands from step 3 above

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `'git' is not recognized` | Download the ZIP instead (above) |
| `ModuleNotFoundError: cvxopt` | `pip install cvxopt` |
| `ModuleNotFoundError: PyQt5` | `pip install PyQt5` |
| `ModuleNotFoundError: click` | `pip install click` |
| `ModuleNotFoundError: pyDRTtools` | You are not in the project folder. `cd` into the folder that contains `launch.py`. |
| `No matching distribution found` for scipy/numpy/pandas | Your Python is 3.12 or newer. Install Python 3.10 and repeat. |
| GUI doesn't open | Use Python 3.10 or 3.11, not 3.12+. Run `python launch.py` from a console so the error is visible. |
| Windows cannot access the file / blocked by policy | This affects the prebuilt `DRTxECM.exe`. Running from source with Python usually works, because `python.exe` is signed. |

## Prebuilt builds instead

If you would rather not install Python at all, use `DRTxECM-win64.zip` from the
same [releases page](https://github.com/Linch-Lab/DRTxECM/releases/latest).
It bundles everything but is a much larger download (~126 MB), and because it is
unsigned some managed machines refuse to run it.
