@echo off
setlocal
py -m pip install --upgrade pip pyinstaller -r requirements.txt || exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DuxTicketPellegrini --add-data "print_ticket.ps1;." app.py || exit /b 1
echo Ejecutable generado en dist\DuxTicketPellegrini.exe
echo Para generar instalador: compilar installer.iss con Inno Setup 6.
