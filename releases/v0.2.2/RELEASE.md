# DRTxECM v0.2.2

修正版。只處理一件事：**Python 版的啟動器與說明文件，在使用者用錯 Python 版本時給不出有用的訊息。**

## 修正

### 啟動器不再信任來路不明的 `.venv`

`START-HERE.bat` 現在會檢查現有 `.venv` 裡的直譯器版本，不是 3.10／3.11 就**自動重建**，而不是看到標記檔就直接啟動。中斷留下的半成品 `.venv` 也會先清掉。

### `INSTALL.md` 原本會把人帶進坑裡

舊版寫的是：

```bat
python -m venv .venv
```

在同時裝了新舊 Python 的機器上，`python` 很可能指到最新的那一個。使用者因此得到一個由 Python 3.15 建立的環境，接著 pip 給出一整串難以理解的錯誤：

```
ERROR: Ignored the following versions that require a different python version:
   ... 1.10.0 Requires-Python >=3.8,<3.12 ...
ERROR: No matching distribution found for scipy==1.10.4
BackendUnavailable: Cannot import 'setuptools.build_meta'
```

現已改用 `py -3.10`，並在文件中說明這個失敗特徵——`cp315`／`cp313` 這類 wheel 標籤、`numpy-1.24.1.tar.gz`（被迫從原始碼編譯）、以及 `BackendUnavailable`。

### `READ-ME-FIRST.txt` 加入同樣的症狀

並明確寫出：**不要去改 `requirements.txt` 的版本號**。

「scipy 1.10.0 好像下載不到」幾乎都是因為 Python 太新——pip 依 `Requires-Python` 把 1.10.0 濾掉了（它宣告只支援 3.8–3.11），所以看起來像版本不存在。改版本號只會讓後面的錯誤更難查，因為同一份清單裡 numpy 1.24.1、pandas 1.5.3、matplotlib 3.7.3 也一樣沒有新 Python 的安裝檔。

## 為什麼 Python 3.15 無論如何都不行

查 PyPI 的實際供應：**cvxopt 在所有發行版本裡，cp315 的 wheel 數量是 0。** 所以在 Python 3.15 上，無論用鎖定的舊版本或各套件的最新版，都會被迫從原始碼編譯 cvxopt 而失敗（需要 C 編譯器與 BLAS／LAPACK）。

| Python | 鎖定版本（scipy 1.10／numpy 1.24） | 各套件最新版 |
|---|---|---|
| 3.10 / 3.11 | 可用 | 部分 |
| 3.12 / 3.13 / 3.14 | 不可用 | 可用 |
| 3.15 | 不可用 | **不可用（cvxopt）** |

本版仍然只支援 **3.10／3.11**（已完整測試的組合）。支援 3.12–3.14 需要另一組依賴清單與 Stage 2／Stage 3 的數值驗證，列為後續工作。

> 附帶說明：我另外實測過 **Python 3.13 + 各套件最新版**（numpy 2.5.4／scipy 1.18.1／pandas 3.1.0），DRT 計算結果與鎖定的 3.10 版本**逐位相同**，GUI 也能正常啟動。所以放寬版本是可行的，只是還沒做進發行檔。

## 升級方式

- **免安裝版**：解壓覆蓋即可。
- **Python 版**：解壓覆蓋。若之前建過 `.venv`，啟動器現在會自動檢查，版本不對就重建；也可以手動刪除 `.venv` 再雙擊 `START-HERE.bat`。

## 下載

| 檔案 | 說明 |
|---|---|
| `DRTxECM-win64.zip` | 免安裝版，不需 Python |
| `DRTxECM-python.zip` | Python 版，需 Python 3.10／3.11 |
| `SHA256SUMS.txt` | 兩個 ZIP 的雜湊值 |

## 已知限制

- 執行檔**未簽章**。若電腦由組織管理、政策只允許簽章程式，免安裝版可能無法執行，請改用 Python 版。
- Python 版第一次啟動需要連上 PyPI 下載約 150 MB 的套件。若網路封鎖 PyPI，請改用免安裝版。
- Python 3.15 不受支援（原因見上）。
