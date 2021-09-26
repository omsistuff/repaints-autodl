python setup.py build
pyinstaller installer.py -F -c -n "omsistuff_autodl_setup.exe" --icon=icon.ico --add-data "icon.ico;." --noconsole
cd build
cd exe*
tar -cvf ../build.zip *
pause