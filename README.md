# DRTxECM

> **DRT × ECM: A pyDRTtools Extension for CPE Phase-Angle-Aware Equivalent Circuit Modeling**

DRTxECM extends [pyDRTtools](https://github.com/ciuccislab/pyDRTtools) with a complete three-stage pipeline: **DRT deconvolution → Gaussian peak decomposition → Complex Nonlinear Least Squares (CNLS) equivalent circuit fitting**. It is the first open-source tool to bridge DRT analysis with ECM parameter estimation, featuring CPE phase-angle as a free fitting parameter.

---

## ✨ What's New in DRTxECM

### Three-Stage Workflow

```
EIS Data → DRT (pyDRTtools) → Gaussian Decomposition → ECM CNLS Fitting
```

| Stage | Module | Description |
|-------|--------|-------------|
| **1. Import & Clean** | `DataImportPreprocessor` / `DataCleaningWindow` | Flexible CSV/TXT import with skip-rows; interactive click-to-remove noise on Nyquist plot; PCHIP interpolation for uniform log-frequency grid |
| **2. DRT → R//CPE** | Gaussian Peak Deconvolution (`Stage2Window`) | Multi-Gaussian fitting of DRT γ(τ); automatic conversion to RC initial parameters (R, C, f_c per peak); one-click export to Stage 3 with R//CPE seeding (initial α = 1.0) |
| **3. ECM Fitting** | CNLS Optimization (`Stage3Window`) | ZView-style parameter table; LR₀ + Σ(Rᵢ//CPEᵢ) circuit model; L-BFGS-B optimization with boundary constraints; real-time Nyquist + Bode preview; branch-resolved visualization |

### Key Innovations

- **CPE Phase-Angle (α) as Free Parameter** — Unlike commercial tools that fix or restrict α, DRTxECM optimizes it alongside R and Q, with bounds 0.2 ≤ α ≤ 1.05
- **DRT-Seeded Initial Guess** — Gaussian peak parameters from DRT provide physics-informed starting values, avoiding random initialization
- **Branch-Resolved Visualization** — Each R//CPE branch rendered in distinct color on Nyquist plot, showing individual semicircle contributions
- **100% Backward Compatible** — All original pyDRTtools DRT computation (Tikhonov regularization, Bayesian, BHT, GP-DRT) is preserved unchanged

---

## Installation

DRTxECM builds on pyDRTtools. Install dependencies:

```bash
conda create --name DRT pip ipython pandas matplotlib scikit-learn spyder
conda activate DRT
pip install cvxopt PyQt5
```

Clone and run:

```bash
git clone https://github.com/Linch-Lab/DRTxECM.git
cd DRTxECM
python launch.py
```

---

## Usage

1. **Import EIS data** — CSV or TXT, with flexible row-skipping for instrument-specific headers
2. **Run DRT** — Use pyDRTtools' Tikhonov, Bayesian, or BHT modes (unchanged)
3. **Deconvolve peaks** — Fit Gaussian peaks to γ(τ); adjust amplitude, position, width
4. **Fit ECM** — Tune R, Q, and **α** for each R//CPE branch via CNLS optimization
5. **Export** — Save fitted parameters, Nyquist/Bode plots, and branch contributions

---

## pyDRTtools — Original Credits

DRTxECM is built on [pyDRTtools](https://github.com/ciuccislab/pyDRTtools) by the Ciucci Lab. All original DRT computation methods are preserved. Please cite the following when using DRTxECM:

[1] Wan, T. H., Saccoccio, M., Chen, C., & Ciucci, F. (2015). *Electrochimica Acta*, 184, 483-499. [DOI](https://doi.org/10.1016/j.electacta.2015.09.097)

[2] Maradesa, A., Py, B., Wan, T.H., Effat, M.B., & Ciucci, F. (2023). *J. Electrochem. Soc.*, 170, 030502. [DOI](https://doi.org/10.1149/1945-7111/acbca4)

[3] Ciucci, F., & Chen, C. (2015). *Electrochimica Acta*, 167, 439-454. [DOI](https://doi.org/10.1016/j.electacta.2015.03.123)

[4] Effat, M. B., & Ciucci, F. (2017). *Electrochimica Acta*, 247, 1117-1129. [DOI](https://doi.org/10.1016/j.electacta.2017.07.050)

[5] Liu, J., Wan, T. H., & Ciucci, F. (2020). *Electrochimica Acta*, 357, 136864. [DOI](https://doi.org/10.1016/j.electacta.2020.136864)

---

## License

MIT License. DRTxECM extensions © Linch-Lab. Original pyDRTtools © Ciucci Lab.
