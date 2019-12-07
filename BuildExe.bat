set path_to_python_virtual_environment=D:\venv3
IF EXIST dist\ (rd /s /q dist)
IF EXIST build\ (rd /s /q build)
IF EXIST encryption.spec (del /s /q encryption.spec)
%path_to_python_virtual_environment%\Scripts
pyinstaller --onefile --hiddenimport pandas --hiddenimport babel.numbers -p %path_to_python_virtual_environment%\Lib\site-packages .\encryption.py