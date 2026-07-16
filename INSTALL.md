# Installing DRTxECM on Windows

## Option A: One-Click (Recommended)

1. Install **Anaconda** from https://www.anaconda.com/download
2. Open **Anaconda Prompt** (Start Menu → Anaconda Prompt)
3. Run:

```bash
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM
conda create --name DRT python=3.10 pip pandas matplotlib scikit-learn spyder -y
conda activate DRT
pip install cvxopt PyQt5
python launch.py
```

## Option B: Without Anaconda (Python Only)

1. Install **Python 3.10+** from https://www.python.org/downloads/ (check "Add to PATH")
2. Open **Command Prompt** (Win+R → `cmd`)
3. Run:

```bash
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM
pip install numpy scipy pandas matplotlib scikit-learn cvxopt PyQt5
python launch.py
```

## Option C: No Git (Download ZIP)

1. Go to https://github.com/Linch-Lab/DRTxECM
2. Click **Code → Download ZIP**
3. Extract to any folder (e.g. `C:\DRTxECM`)
4. Open Anaconda Prompt or Command Prompt
5. `cd C:\DRTxECM\DRTxECM-master`
6. Follow steps from Option A or B for dependencies
7. `python launch.py`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `git` not found | Use Option C (Download ZIP) |
| `ModuleNotFoundError: cvxopt` | `pip install cvxopt` |
| `ModuleNotFoundError: PyQt5` | `pip install PyQt5` |
| GUI doesn't open | Try `conda activate DRT` first |
| Chinese text in UI | Fixed in latest version — re-download |
