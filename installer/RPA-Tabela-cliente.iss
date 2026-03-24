#define AppId "{{E6D1B33D-95E0-4AD5-B5A1-3AF59A36D0EE}"
#define AppName "RPA-Tabela-cliente"
#define AppVersion "1.0.0"
#define AppPublisher "Rodogarcia"
#define AppExeName "RPA-Tabela-cliente.exe"
#define AppDistDir "..\\dist\\RPA-Tabela-cliente"
#define AppIcon "..\\public\\app-icon.ico"
#define InstallerOutput "..\\dist\\instalador"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Rodogarcia\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#InstallerOutput}
OutputBaseFilename={#AppName}-Setup
SetupIconFile={#AppIcon}
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
CloseApplications=yes
CloseApplicationsFilter={#AppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos adicionais:"

[Files]
Source: "{#AppDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\_internal\public\app-icon.ico"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; IconFilename: "{app}\_internal\public\app-icon.ico"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent
