# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['restim.py'],
    pathex=['.'],
    binaries=[],
    datas=[('resources/favicon.png', 'resources/'), ('resources/phase diagram bg.svg', 'resources/'), ('event_definitions', 'qt_ui/event_definitions')],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'pynput._util.win32'],
    hookspath=['pyinstaller-hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='restim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\favicon.ico'],
)
