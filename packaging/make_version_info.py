# -*- coding: utf-8 -*-
"""
由 version.txt 產生 PyInstaller 需要的 Windows 版本資源檔。

PyInstaller 的 --version-file / EXE(version=...) 吃的是一種 Python 語法的
結構描述（VSVersionInfo），格式繁瑣且容易和版本號不同步。這裡改成每次
建置時從 version.txt 生成，讓 version.txt 維持「版本號唯一來源」。

輸出：packaging/version_info.txt
用法：python packaging/make_version_info.py
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VERSION_FILE = os.path.join(REPO, "version.txt")
OUT_FILE = os.path.join(HERE, "version_info.txt")

APP_NAME = "DRTxECM"
COMPANY = "Linch-Lab"
DESCRIPTION = "DRTxECM - DRT to Equivalent Circuit Modeling for EIS data"

# 0x0409 = en-US，1200 = Unicode。學術工具的發行檔用英文語系最通用。
LANG_ID = "040904B0"
TRANSLATION = "0x0409, 1200"

TEMPLATE = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v0}, {v1}, {v2}, {v3}),
    prodvers=({v0}, {v1}, {v2}, {v3}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('{lang}', [
        StringStruct('CompanyName', '{company}'),
        StringStruct('FileDescription', '{desc}'),
        StringStruct('FileVersion', '{ver}'),
        StringStruct('InternalName', '{app}'),
        StringStruct('LegalCopyright', 'MIT License'),
        StringStruct('OriginalFilename', '{app}.exe'),
        StringStruct('ProductName', '{app}'),
        StringStruct('ProductVersion', '{ver}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [{trans}])])
  ]
)
"""


def read_version():
    """讀取 version.txt 並正規化成四個數字。"""
    try:
        with open(VERSION_FILE, encoding="utf-8") as f:
            raw = f.read().strip()
    except OSError as exc:
        raise SystemExit(f"讀不到 {VERSION_FILE}：{exc}")

    m = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?$", raw)
    if not m:
        raise SystemExit(f"version.txt 的內容不是版本號：{raw!r}")

    parts = [int(g) if g is not None else 0 for g in m.groups()]
    return raw, parts


def main():
    ver, parts = read_version()
    body = TEMPLATE.format(
        v0=parts[0], v1=parts[1], v2=parts[2], v3=parts[3],
        lang=LANG_ID, trans=TRANSLATION,
        company=COMPANY, desc=DESCRIPTION, ver=ver, app=APP_NAME,
    )
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"wrote {OUT_FILE} (version {ver} -> {parts})")


if __name__ == "__main__":
    main()
