# 發行版本（releases/）

每個發行版本各自一個以版本號命名的資料夾。

```
releases/
├── README.md              本文件
├── v0.2.1/
│   ├── DRTxECM-win64.zip  免安裝，解壓即用（不進版控，走 GitHub Releases）
│   ├── SHA256SUMS.txt     檔案雜湊，可驗證下載完整性
│   └── RELEASE.md         版本說明與更新重點
└── v0.3.0/                （未來版本）
```

## 怎麼產生

於倉庫根目錄執行 `build.bat`，會自動：

1. 從 `version.txt` 讀取版本號（**版本號的唯一來源**）
2. 從 `version.txt` 生成 `packaging\version_info.txt`（Windows 檔案內容的版本資訊）
3. 用 PyInstaller 依 `DRTxECM.spec` 建置 `dist\DRTxECM\DRTxECM.exe`
4. 打包成 `releases\v<版本>\DRTxECM-win64.zip`
5. 產生同資料夾的 `SHA256SUMS.txt`

## 中間產物 vs. 正式產物

| 位置 | 性質 | 處置 |
|---|---|---|
| `build\` | PyInstaller 工作資料夾 | 中間產物，可刪 |
| `dist\` | 建置輸出（測試用） | 中間產物，可刪 |
| `packaging\version_info.txt` | 自動生成的版本資源 | 中間產物，可刪 |
| **`releases\`** | **正式保存的發行說明** | **保留** |

`build.bat` 每次都會用 `--clean` 重建，所以直接刪掉 `build\`、`dist\` 是安全的。

## 版控原則

**二進位檔不進 git**，一律走 GitHub Releases。`.gitignore` 因此排除了：

```
releases/*/DRTxECM-win64/
releases/*/*.zip
packaging/version_info.txt
```

實際納入版控的只有版本說明與雜湊值：

| 檔案 | 進版控 |
|---|---|
| `releases/README.md` | 是 |
| `releases/v0.2.1/RELEASE.md` | 是 |
| `releases/v0.2.1/SHA256SUMS.txt` | 是 |
| `releases/v0.2.1/DRTxECM-win64.zip` | 否（走 Releases） |

## 發佈流程

```bat
build.bat                          :: 產生 releases\v0.2.1\
git add releases\v0.2.1\RELEASE.md
git commit -m "Release v0.2.1"
git tag v0.2.1
git push origin master
git push origin v0.2.1             :: GitHub Actions 自動建置並發佈 Release
```

推送標籤後，`.github/workflows/release.yml` 會在 GitHub 上自動：

1. 用 Python 3.10 安裝依賴
2. 建置 `DRTxECM.exe`
3. **用 offscreen 模式實際啟動一次程式**，確認打包檔不會一開就崩潰
4. 壓成 `DRTxECM-win64.zip`、產生 `SHA256SUMS.txt`
5. 建立 GitHub Release

網站上的下載連結指向 `releases/latest/download/DRTxECM-win64.zip`，
所以不需要把 zip 提交進 git。

> **順序很重要**：網站下載按鈕連到 GitHub 的 `releases/latest`。
> 在第一次推送標籤、Release 出現之前，那個網址會是 404。
> 請先完成一次發佈，再對外公開網站。
