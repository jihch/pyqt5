# pyqt5

##### 1.确保 .ico 文件跟源码文件在同一目录下<br><br>

##### 2.代码中配置 ico 文件
```python
window.setWindowIcon(QIcon(":/icon.ico"))
```
<br>

##### 3.新建资源文件 resources.qrc
```
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource>
        <file alias="icon.ico">icon.ico</file><!-- 使用 ICO 格式 -->
    </qresource>
</RCC>
```
<br>

##### 4.编辑资源文件，这一步会生成 resources.py 文件
```
pyrcc5 resources.qrc -o resources.py
```
<br>

##### 5.创建 spec 配置文件
```
# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources.py', '.'), ('icon.ico', '.')],
    hiddenimports=['PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Base64Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
```
<br>

##### 6.打包到一个可执行文件
```
pyinstaller --name=Base64Converter --onefile --windowed --icon=icon.ico --add-data="resources.py;." --add-data="icon.ico;." --hidden-import=PyQt5.sip main.py
```