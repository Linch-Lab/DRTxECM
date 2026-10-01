# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 設定 —— 把 DRTxECM 打包成 Windows 免安裝版本。

用法（在倉庫根目錄執行）：

    python -m PyInstaller --noconfirm DRTxECM.spec

產出：

    dist/DRTxECM/DRTxECM.exe    可直接執行的程式（onedir）

為什麼用 onedir 而不是 onefile
    onefile 每次啟動都要把整包解壓到暫存資料夾，本專案會載入
    PyQt5 + matplotlib + scipy + sklearn，解壓要好幾秒。onedir
    啟動快，也讓防毒軟體少一點誤判。打包成 ZIP 後一樣是單一檔案下載。

為什麼不需要 --add-data
    應用程式的資料檔（EIS 的 CSV/TXT、手冊 PDF）全部由使用者透過
    檔案對話框選取，程式本身不做任何相對於 __file__ 的資源載入，
    因此沒有需要一起打包的靜態資源。

注意
    本檔案由建置流程使用；`version` 與 `icon` 這兩個路徑若不存在會
    自動略過，所以單獨跑 PyInstaller 也不會壞掉。
"""

import os

from PyInstaller.utils.hooks import collect_all

APP_NAME = "DRTxECM"
SPEC_DIR = os.path.abspath(SPECPATH)

# ---------------------------------------------------------------------------
# cvxopt 除了自身的 .pyd 之外還夾帶 BLAS/LAPACK 的 DLL。內建 hook 不一定會
# 全部收進來，缺 DLL 會在「執行 DRT 擬合」當下才爆掉，因此明確收集。
# ---------------------------------------------------------------------------
cvxopt_datas, cvxopt_binaries, cvxopt_hidden = collect_all("cvxopt")

hiddenimports = cvxopt_hidden + [
    # matplotlib 的 Qt 後端是在執行期以字串指定（mpl.use("Qt5Agg")），
    # 靜態分析看不到，必須手動指定。
    "matplotlib.backends.backend_qt5agg",
    "matplotlib.backends.backend_agg",
    "PyQt5.QtPrintSupport",
    # scikit-learn 的 Cython 子模組（只有 KFold 會用到，但 sklearn 的
    # 相依鏈常需要這幾個）
    "sklearn.model_selection",
    "sklearn.utils._cython_blas",
    "sklearn.utils._typedefs",
    "sklearn.neighbors._partition_nodes",
    "sklearn.tree._utils",
]

# 只排除確定用不到的重量級套件。刻意「不」排除 setuptools/pkg_resources，
# 因為 scipy / sklearn 在部分版本會在執行期用到它。
excludes = [
    "tkinter",
    "PyQt6",
    "PySide2",
    "PySide6",
    "IPython",
    "jupyter",
    "notebook",
    "nbformat",
    "pytest",
    "sphinx",
    "docutils",
    "pip",
]

_icon = os.path.join(SPEC_DIR, "assets", "DRTxECM.ico")
_version_file = os.path.join(SPEC_DIR, "packaging", "version_info.txt")

a = Analysis(
    ["launch.py"],
    pathex=[SPEC_DIR],
    binaries=cvxopt_binaries,
    datas=cvxopt_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX 壓縮會讓部分防毒軟體更容易誤判，且 CI runner 預設沒有 UPX。
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon if os.path.exists(_icon) else None,
    version=_version_file if os.path.exists(_version_file) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)
