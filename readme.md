Build program
```bat
python setup.py build
```

Build installer
```bat
pyinstaller installer.py -F -c -n "omsistuff_autodl_setup.exe" --icon=icon.ico --add-data "icon.ico;." --noconsole
```