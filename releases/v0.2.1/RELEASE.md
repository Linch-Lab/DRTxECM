# DRTxECM v0.2.1

第二個公開發行版本。這一版的主題是**讓使用者在各種環境下都拿得到、也跑得起來**。

## 新增

### Python 版（新的下載選項）

`DRTxECM-python.zip`，約 1.8 MB（免安裝版是 126 MB，小約 69 倍）。

從原始碼執行的版本，內含啟動器 `START-HERE.bat`：自動尋找 Python 3.10／3.11、
建立專用的 `.venv`、安裝並驗證套件，然後啟動程式。另附 `DEBUG.bat`
（保留主控台以顯示真正的錯誤）與中文的 `READ-ME-FIRST.txt`。

**為什麼需要它**：`DRTxECM.exe` 沒有程式碼簽章，學校或公司的政策
（AppLocker／WDAC／集中管理的端點防護）可能直接拒絕啟動它。`python.exe`
是簽章過的程式，因此「用已簽章的直譯器執行未簽章的原始碼」在許多政策下可以通過。

### 免安裝版附上診斷工具

- `診斷.cmd`：檢查檔案完整性、路徑長度、下載封鎖標記、AppLocker／WDAC 政策、
  主要防毒產品、以及執行檔本身的 SHA256
- `使用前必讀.txt`：六個最常見的啟動失敗原因與逐步排除方式

## 修正

- **`requirements.txt` 補上 `click`。** `pyDRTtools/__init__.py` 會匯入
  `pyDRTtools.cli`，而 `cli.py` 匯入 `click`；少了它，照文件安裝出來的程式
  一啟動就是 `ModuleNotFoundError`。
- **`INSTALL.md` 重寫。** 原本的指令漏了 `click`，而且寫「Python 3.10+」——
  但鎖定的 scipy 1.10／numpy 1.24／pandas 1.5 沒有 3.12 以上的 wheel，
  照著做會直接進入幾乎必然失敗的原始碼編譯。
- **`build.bat` 與 `診斷.cmd` 改為 CRLF。** git 預設把文字 blob 存成 LF，
  而 cmd.exe 對只有 LF 的批次檔會誤判（多行 `if` 區塊與 `for /f` 迴圈）。
  已加 `.gitattributes`（`*.bat`／`*.cmd` 標為 `-text`）讓這些檔案保持原始位元組，
  從 GitHub 直接下載也不會拿到 LF 版本。

## 發佈流程的強化

- CI 會在壓縮前**實際匯入** `pyDRTtools`，並檢查兩支 .bat 是純 ASCII 且為 CRLF。
  這道關卡來自測試時抓到的真實缺陷：套件目錄是 `pyDRTtools`（大寫 T），
  但 Windows 的 `Copy-Item` 不分大小寫，打錯字會靜默建立 `pyDRtTools`，
  而 CPython 的 import 路徑快取**區分大小寫**，結果整包無法匯入。
- `SHA256SUMS.txt` 現在同時包含兩個 ZIP 的雜湊值。

## 下載

| 檔案 | 說明 |
|---|---|
| `DRTxECM-win64.zip` | 免安裝版，不需 Python，約 126 MB |
| `DRTxECM-python.zip` | Python 版，需 Python 3.10 或 3.11，約 1.8 MB |
| `SHA256SUMS.txt` | 兩個 ZIP 的雜湊值 |

## 已知限制

- 執行檔**未簽章**。若電腦由組織管理、且政策只允許簽章程式，免安裝版可能無法執行，
  請改用 Python 版。
- Python 版第一次啟動需要連上 PyPI 下載約 150 MB 的套件。若學校封鎖 PyPI，
  請改用免安裝版。兩者剛好互補。
- 尚未提供 macOS／Linux 的預先建置版本，該平台請從原始碼執行。
