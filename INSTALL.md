# DRTxECM Installation & Quick Start

## 1. Clone & Install

```bash
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM

# Create conda environment
conda create --name DRT python=3.10 pip -y
conda activate DRT

# Install dependencies
pip install numpy scipy pandas matplotlib scikit-learn cvxopt PyQt5

# Launch
python launch.py
```

## 2. Minimal Example (Python API)

```python
from pyDRTtools.runs import DRT
from pyDRTtools.extensions import ecm_circuit_solver
import pandas as pd

# Load EIS data
df = pd.read_csv("your_data.csv")  # columns: freq, Z_re, Z_im
freq = df.iloc[:,0].values
Z = df.iloc[:,1].values + 1j*df.iloc[:,2].values

# Run DRT (Stage 1)
drt = DRT(freq, Z)
drt.run_simple()

# ECM fitting (Stage 2-3 via GUI or API)
```

## 3. GUI Workflow

1. `python launch.py`
2. File → Import EIS data (CSV/TXT)
3. Click **DRT Analysis** → Select regularization method
4. After DRT, click **Stage 2: Gaussian Decomposition**
5. Adjust peaks → Click **Export to Stage 3**
6. **Stage 3: ECM Fitting** → Tune R, Q, α → Click **Optimize**

## 4. Requirements

- Python >= 3.10
- OS: Windows / macOS / Linux
- RAM: 4 GB minimum
