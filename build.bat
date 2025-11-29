@echo off
echo  Kompilowanie przeglądarki Xilan...
pyinstaller --onefile --windowed --icon=icon.ico --name=XilanWebBrowser main.py
echo Kompilacja zakończona!
pause
