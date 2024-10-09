# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('resources/phase diagram bg.svg', 'resources/'),
    ('resources/favicon.png', 'resources/')
]

a = Analysis(
    ['restim.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='restim_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
//    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/favicon.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='restim'
)

app = BUNDLE(
    coll,
    name='restim.app',
    icon='resources/favicon.png',
    bundle_identifier=None,
    info_plist={
        'NSHighResolutionCapable': 'True'
    },
)

