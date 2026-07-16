# Installing DRTxECM on Windows

## Quick Install

1. Install **Python 3.10+** from https://www.python.org/downloads/ (tick "Add to PATH")
2. Open **Command Prompt** (Win+R → `cmd`)
3. Run:

```bash
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM
pip install numpy scipy pandas matplotlib scikit-learn cvxopt PyQt5
python launch.py
```

## No Git? Download ZIP

1. https://github.com/Linch-Lab/DRTxECM → **Code → Download ZIP**
2. Extract anywhere, open Command Prompt in that folder
3. Same install: `pip install numpy scipy pandas matplotlib scikit-learn cvxopt PyQt5`
4. `python launch.py`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `'git' is not recognized` | Download ZIP instead |
| `ModuleNotFoundError: cvxopt` | `pip install cvxopt` |
| `ModuleNotFoundError: PyQt5` | `pip install PyQt5` |
| GUI doesn't open | Use Python 3.10, not 3.12+ |
