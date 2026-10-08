# 打包成 Windows 免安裝版（packaging/）

本站交付的「免安裝 Windows 版」由 PyInstaller 打包而成。使用者下載
`DRTxECM-win64.zip`、解壓、執行 `DRTxECM.exe` 即可，**不需要安裝 Python**。

## 為什麼建置環境固定用 Python 3.10

上游 `requirements.txt` 把版本鎖在：

```
scipy==1.10.0
numpy==1.24.1
pandas==1.5.3
PyQt5==5.15.9
matplotlib==3.7.3
```

其中 scipy 1.10 / numpy 1.24 / pandas 1.5 **都沒有 Python 3.12 以上的
wheel**（PyPI 上找不到對應的 cp312/cp313 檔案），硬裝會退化成本機編譯，
在 CI 上幾乎一定失敗。上游 `INSTALL.md` 的疑難排解也直接寫明
「GUI doesn't open → Use Python 3.10, not 3.12+」。

因此 `packaging/requirements-build.txt` 與 CI 都使用 **Python 3.10**。
本機若預設是 3.12／3.13，請明確指定：

```bat
py -3.10 -m venv .venv
.venv\Scripts\activate
```

## 本機建置

```bat
build.bat
```

它會依序：讀 `version.txt` → 生成 `packaging\version_info.txt` →
安裝依賴 → PyInstaller 建置 → 打包 zip → 產生 SHA256。

中途產物在 `build\` 與 `dist\`，可以隨時刪除；正式產物在
`releases\v<版本>\`。

想跳過 `build.bat` 手動跑也可以：

```bat
python packaging\make_version_info.py
python -m PyInstaller --noconfirm --clean DRTxECM.spec
```

## 打包設定重點（DRTxECM.spec）

| 項目 | 說明 |
|---|---|
| `onedir`（非 onefile） | PyQt5 + matplotlib + scipy 解壓要好幾秒；onedir 啟動快，防毒誤判也較少 |
| `--collect-all cvxopt` | cvxopt 夾帶 BLAS/LAPACK 的 DLL，內建 hook 不一定全收，缺了會在跑 DRT 擬合時才崩潰 |
| `matplotlib.backends.backend_qt5agg` | 後端是用 `mpl.use("Qt5Agg")` 字串指定，靜態分析看不到，必須手動列為 hidden import |
| 不需要 `--add-data` | 程式不做任何相對於 `__file__` 的資源載入；EIS 資料檔全由使用者透過檔案對話框選取 |
| `upx=False` | UPX 壓縮會提高防毒誤判率，且 CI runner 預設沒有 UPX |
| `console=False` | 視窗模式，不彈出黑色命令列視窗 |

`DRTxECM.spec` 裡 `icon` 與 `version` 兩個路徑若不存在會自動略過，
所以單獨跑 PyInstaller 也不會因為缺檔而失敗。

## 隨發行檔附上的說明與診斷工具（packaging/extras/）

`DRTxECM.exe` **沒有程式碼簽章**（見下方說明），所以使用者的電腦若是學校或公司
管理，可能被政策或防毒阻擋。為了讓被擋的使用者有事可做、有東西可回報，
`build.bat` 與 CI 都會把 `packaging/extras/` 的內容複製到 `dist\DRTxECM\`，
也就是解壓後與 `DRTxECM.exe` 同層：

| 檔案 | 用途 |
|---|---|
| `使用前必讀.txt` | 六個最常見的「無法啟動」原因與排除步驟（UTF-8 **with BOM**，確保記事本不亂碼） |
| `診斷.cmd` | 環境診斷。印出檔案完整性、路徑長度、封鎖標記、AppLocker／WDAC 政策、防毒狀態與偵測紀錄 |

複製一定發生在壓縮之前，否則檔案不會進到 ZIP 裡。

### `診斷.cmd` 的設計限制

- **必須維持純 ASCII**（內容，不是檔名）。理由與 `build.bat` 相同：cmd.exe 用系統
  ANSI 碼頁讀 .cmd，非 ASCII 位元組會讓它讀錯前面的行。
- 它**只讀取設定**，唯一會修改東西的地方是詢問是否解除「已封鎖」標記，預設是 N。
- 輸出刻意使用 ISO 時間格式與非在地化的欄位，因為使用者會把輸出貼到 GitHub
  Issue；在地化字串（例如 `%DATE%`、OS 的顯示名稱）在別人的瀏覽器上會變亂碼。

### 為什麼不直接簽章

程式碼簽章憑證是付費的（OV 約每年數百美元），而且 2023 年 6 月起私鑰必須存放於
FIPS 140-2 硬體模組，成本與流程都更高。在那之前，實務上的做法是：
提供清楚的排除說明、一支診斷工具，並在網站上說明「學校電腦可能無法執行未簽章程式」
這件事——因為那是政策問題，不是程式問題。

## 第二個發行版本：Python 版（packaging/python-edition/）

除了免安裝版，每個 Release 還會附上一個**從原始碼執行**的版本
`DRTxECM-python.zip`。它不是建置產物，而是把倉庫內容加上三支使用者檔案打包：

| 檔案 | 用途 |
|---|---|
| `START-HERE.bat` | 啟動器。找 Python → 建 `.venv` → 裝套件 → 驗證 → 啟動 |
| `DEBUG.bat` | 同上但保留主控台，用來顯示程式真正的錯誤訊息 |
| `READ-ME-FIRST.txt` | 中文說明（UTF-8 **with BOM**，記事本不亂碼） |

### 為什麼需要這個版本

`DRTxECM.exe` 沒有程式碼簽章，所以學校或公司的 AppLocker／WDAC／端點防護
可能直接擋掉它。**`python.exe` 是簽章過的**，因此「用已簽章的直譯器執行
未簽章的原始碼」這種組合，在許多政策下是可以通過的。

另外它只有約 2.6 MB，而免安裝版是 126 MB（差 47 倍）。

代價是**第一次啟動需要網路**：要從 PyPI 下載約 150 MB 的套件。
如果學校封鎖 PyPI，這個版本就裝不起來——那種情況請改用免安裝版。
兩者剛好互補：

| 情況 | 該用哪個版本 |
|---|---|
| 一般使用者 | 免安裝版 |
| 電腦會阻擋未簽章程式 | **Python 版** |
| 學校封鎖 PyPI | **免安裝版** |
| 頻寬有限 | **Python 版** |

### 兩個踩過的坑（都已修掉，請勿改回去）

**1. 目錄大小寫必須是 `pyDRTtools`（大寫 T）。**
`launch.py` 寫的是 `from pyDRTtools.GUI import ...`。Windows 的檔案系統不分大小寫，
所以 `Copy-Item` 就算路徑打錯成 `pyDRtTools` 也會成功——但**會用錯誤的大小寫
建立目的目錄**。而 CPython 的 import 路徑快取是**區分大小寫**的，結果就是
`ModuleNotFoundError: No module named 'pyDRTtools'`。
CI 因此多了一步「Verify the source edition」，會在壓縮前真的執行
`python -c "import pyDRTtools"`，這類錯誤就不會再出貨。

**2. `.bat` 必須純 ASCII 且 CRLF。**
純 ASCII 的理由同 `build.bat`；CRLF 的理由是 cmd.exe 對只有 LF 的批次檔會誤判
（多行 `if` 區塊與 `for /f` 迴圈）。CI 的驗證步驟與 `tools/check_site.py`
都會檢查這兩點。

> 也因為「純 ASCII」這條規則，`START-HERE.bat` 裡不能出現中文檔名——
> 所以使用者說明的檔名是 ASCII 的 `READ-ME-FIRST.txt`（內容仍是中文），
> 需要解釋時由 .bat 呼叫 `notepad` 開啟它。

### 其他設計取捨

- **用 `.venv` 而不是直接 `pip install`**：不需要系統管理員權限，也不會污染
  使用者原本的 Python 環境。整個 `.venv` 資料夾可以刪掉重來。
- **第一次之後就跳過安裝**：靠 `.venv\.installed` 這個標記檔。
  想強制重裝就執行 `START-HERE.bat repair`。
- **啟動用 `pythonw.exe`**：不會留下黑色主控台視窗。需要看訊息時改跑
  `DEBUG.bat`（等同 `START-HERE.bat console`）。
- **只接受 Python 3.10 與 3.11**：上游鎖定的 scipy 1.10／numpy 1.24／pandas 1.5
  沒有 3.12+ 的 wheel。版本不對時會給明確訊息，並自動開啟中文說明。

## 版本號的唯一來源

`version.txt`（倉庫根目錄）是**版本號的唯一來源**，內容就是一行版本號：

```
0.2.1
```

`build.bat` 與 GitHub Actions 都讀它；`packaging/make_version_info.py`
再把它轉成 Windows 檔案內容看得到的版本資訊（在檔案總管對
`DRTxECM.exe` 按右鍵 →「內容」→「詳細資料」就看得到）。

> **已知不一致**：上游 `setup.py` 裡的 `version = "0.2"` 是 pip 套件版本，
> 與 `version.txt` 各自獨立。本專案刻意不修改上游既有檔案，因此兩者需要
> 手動同步；若日後要統一，可讓 `setup.py` 改讀 `version.txt`。

## CI 自動發佈

`.github/workflows/release.yml` 在推送 `v*` 標籤時自動建置並發佈。

其中最重要的是 **offscreen 冒煙測試**：PyInstaller 很常「建置成功」卻在
啟動時才因缺少 Qt 平台外掛或 cvxopt 的 DLL 而崩潰。CI 會用
`QT_QPA_PLATFORM=offscreen` 實際啟動 `DRTxECM.exe`、等 30 秒，若行程
已經退出就讓整個流程失敗，不把壞掉的打包檔發佈出去。

## 發佈順序（重要）

網站的下載按鈕指向：

```
https://github.com/Linch-Lab/DRTxECM/releases/latest/download/DRTxECM-win64.zip
```

`releases/latest` 在**還沒有任何 Release 時會回 404**。所以請先：

```bat
git tag v0.2.1
git push origin v0.2.1
```

等 Actions 跑完、Release 出現、確認下載連結可用之後，再把網站對外公開。

## 系統需求

| 項目 | 需求 |
|---|---|
| 作業系統 | Windows 10 / 11（64 位元） |
| Python | **不需要**（已打包） |
| 記憶體 | 建議 8 GB 以上（DRT 擬合涉及大型矩陣運算） |
| 網路 | 不需要（完全離線運算） |
