; Inno Setup Script for PDF Presenter
; Requires: Inno Setup 6 (http://jrsoftware.org/isinfo.php)

#define MyAppName "PDF Presenter"
#define MyAppVersion "3.0"
#define MyAppPublisher "TOUGMA19"
#define MyAppURL "https://github.com/TOUGMA19/PDF-Presenter"
#define MyAppExeName "PDF Presenter.exe"

[Setup]
AppId={{PDF-Presenter-TOUGMA19-v3}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\PDF Presenter
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=dist
OutputBaseFilename=PDF-Presenter-Setup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\PDF Presenter\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PDF Presenter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
