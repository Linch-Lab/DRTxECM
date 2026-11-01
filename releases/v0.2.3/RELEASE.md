# DRTxECM v0.2.3

緊急修正。**v0.2.2 的 Python 版啟動器在「電腦上沒有 Python 3.10／3.11」時，會給出錯誤的訊息。**

## 問題

使用者雙擊 `START-HERE.bat`（v0.2.2）時看到：

```
[ERROR] No runtime installed that matches 3.10. Try running "py install 3.10".
[ERROR] Could not create the Python environment .venv
```

第二行是誤導——真正的原因是第一行：**電腦上根本沒有 Python 3.10**。

原因出在偵測邏輯。新版 Windows 的 `py`（Python Install Manager）在找不到指定版本時，會印出錯誤訊息，**但離開碼仍然是 0（成功）**。舊版啟動器只看離開碼，於是「接受」了一個不存在的 Python，接著拿它去建立 `.venv` 而失敗，最後把錯誤歸因到磁碟空間或防毒。

## 修正

- 偵測程式現在**要求直譯器回報出真正的版本號**，光有離開碼 0 不算通過。讀不到版本就跳過該候選。
- 「找不到 Python」與「版本不對」的訊息現在會**直接給出可執行的指令**：

  ```
  py install 3.10
  ```

  新版 `py` 這一行就會自動安裝。另外也保留從 python.org 下載的作法。
- `.venv` 建立失敗時，會**印出實際使用的直譯器與它回報的版本**，並立刻重跑一次讓真正的錯誤顯示出來，不再只列舉泛泛的可能原因。
- 中文說明文件同步加入 `py install 3.10` 的作法（原本只寫「到 python.org 下載」）。

## 驗證方式

用一支和真實 `py` 行為相同的 .exe 樁（印出同樣的錯誤、離開碼 0）重現：

| 邏輯 | 遇到「假 Python」 | 遇到真正的 3.10 |
|---|---|---|
| v0.2.2（舊） | **接受** → 產生上面那個誤導訊息 | 接受 |
| v0.2.3（新） | **拒絕** → 改為提示安裝 3.10 | 接受 |

另外也實測真實環境仍能正確找到 Python 3.10.11 並繼續建立環境。

## 如果你的電腦上沒有 Python

在命令提示字元輸入：

```
py install 3.10
```

或從 https://www.python.org/downloads/release/python-31011/ 下載安裝檔，
安裝時勾選「Add python.exe to PATH」。裝完再雙擊一次 `START-HERE.bat`。

## 下載

| 檔案 | 說明 |
|---|---|
| `DRTxECM-win64.zip` | 免安裝版，不需 Python |
| `DRTxECM-python.zip` | Python 版，需 Python 3.10／3.11 |
| `SHA256SUMS.txt` | 兩個 ZIP 的雜湊值 |

## 已知限制

- 執行檔**未簽章**；若組織政策只允許簽章程式，免安裝版可能無法執行，請改用 Python 版。
- Python 版第一次啟動需要連上 PyPI 下載約 150 MB 的套件。
- **Python 3.15 不受支援**：cvxopt 沒有任何 cp315 的 wheel，兩條路都會被迫從原始碼編譯而失敗。
