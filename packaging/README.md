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

## 版本號的唯一來源

`version.txt`（倉庫根目錄）是**版本號的唯一來源**，內容就是一行版本號：

```
0.2.0
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
git tag v0.2.0
git push origin v0.2.0
```

等 Actions 跑完、Release 出現、確認下載連結可用之後，再把網站對外公開。

## 系統需求

| 項目 | 需求 |
|---|---|
| 作業系統 | Windows 10 / 11（64 位元） |
| Python | **不需要**（已打包） |
| 記憶體 | 建議 8 GB 以上（DRT 擬合涉及大型矩陣運算） |
| 網路 | 不需要（完全離線運算） |
