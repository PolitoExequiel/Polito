#define MyAppName "Dux Ticket Pellegrini"
#define MyAppVersion "0.2.1"
[Setup]
AppId={{A03F8DF4-6CC0-489E-963A-82CE4D09A99A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\DuxTicketPellegrini
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=DuxTicket_Pellegrini_Instalador_Windows_x64
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
[Files]
Source: "dist\DuxTicketPellegrini.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\Dux Ticket Pellegrini"; Filename: "{app}\DuxTicketPellegrini.exe"
Name: "{autodesktop}\Dux Ticket Pellegrini"; Filename: "{app}\DuxTicketPellegrini.exe"
[Run]
Filename: "{app}\DuxTicketPellegrini.exe"; Description: "Abrir Dux Ticket Pellegrini"; Flags: nowait postinstall skipifsilent
