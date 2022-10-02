pyinstaller --windowed --onefile main.py
cd dist
del 4inarow.exe
rename main.exe 4inarow.exe
cd ..