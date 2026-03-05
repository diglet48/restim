# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['restim.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/phase diagram bg.svg', 'resources/'),
        ('resources/favicon.png', 'resources/'),
        ('event_definitions', 'qt_ui/event_definitions'),
    ],
    hiddenimports=[],
    hookspath=['pyinstaller-hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL._avif'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='restim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/favicon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='restim',
)

app = BUNDLE(
    coll,
    name='restim.app',
    icon='resources/favicon.png',
    bundle_identifier=None,
    info_plist={
        'NSHighResolutionCapable': 'True',
    },
)

